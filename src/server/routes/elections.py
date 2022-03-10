import json
import glob
import base64
import string
import random
from urllib import response
from xml.dom.expatbuilder import CDATA_SECTION_NODE
from pytest import yield_fixture

from electiersa import electiersa
from multiprocessing.sharedctypes import synchronized
import random
import string
import requests
import time
import os
from pprint import pprint

import traceback
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from src.server import config
from src.server import schemas
from src.server.database import DB, get_database
from src.server.database import get_parties_with_candidates, get_max_id
from src.server.routes.elastic import get_parties_and_candidates_lookup
import asyncio

from elasticsearch import Elasticsearch, helpers

# Main elastic search connction
ES = Elasticsearch(hosts= [{"scheme": "http", 'host': os.environ['ELASTIC_HOST'],'port': int(os.environ['ELASTIC_PORT'])}])

# Create FastAPI router
router = APIRouter(
    prefix = "/elections",
    tags = ["Elections"],
)

async def validate_polling_place_id(polling_place_id):
    DB  = await get_database()

    if await DB.key_pairs.count_documents({"polling_place_id":polling_place_id}) == 0:
        content = {
            "status": "failure",
            "message": "Invalid polling place id",
        }
        return content

    content = {
        "status": "success",
        "message": "Polling place id was successfully validated",
    }
    return content


async def validate_party_and_candidates(vote):
    candidate_ids = vote["candidate_ids"]

    if len(candidate_ids) > 5:
        content = {
            "status": "failure",
            "message": "Number of candidates is more than 5",
        }
        return content

    if len(set(candidate_ids)) != len(candidate_ids):
        content = {
            "status": "failure",
            "message": "Duplicate candidates ids",
        }
        return content

    parties = await get_parties_with_candidates()
    for party in parties:
        if party["_id"] == vote["party_id"]:
            candidate_match_count = 0
            for candidate in candidate_ids:
                if candidate in [i["_id"] for i in party["candidates"]]:
                    candidate_match_count += 1

                else:
                    err_msg = f'candidate |{candidate}| is not in party |{party["_id"]}|'

                    content = {
                        "status": "failure",
                        "message": "Invalid candidates ids - " + err_msg,
                    }
                    return content

            content = {
                "status": "success",
                "message": "Parties with candidates were successfully validated",
            }
            return content

    content = {
        "status": "failure",
        "message": "Invalid party id",
    }
    return content


async def validate_tokens(tokens):
    if len(set(tokens)) != len(tokens):
        content = {
            "status": "failure",
            "message": "Duplicate tokens in the batch",
        }
        return content

    content = {
        "status": "success",
        "message": "Tokens were successfully validated",
    }
    return content


async def validate_token_with_polling_place_id(token, polling_place_id):
    DB = await get_database()

    if await DB.votes.count_documents({"token":token, "polling_place_id": polling_place_id}) != 0:
        content = {
            "status": "failure",
            "message": "Duplicate combination of token and polling place id",
        }
        return content
    content = {
        "status": "success",
        "message": "Token was successfully validated",
    }
    return content


async def validate_election_id(election_id):
    if election_id != config.ELECTION_ID:
        content = {
            "status": "failure",
            "message": "Invalid election id",
        }
        return content
    content = {
        "status": "success",
        "message": "Election id was successfully validated",
    }
    return content


async def validate_decryption(decrypted_vote, polling_place_id, max_id, _id):
    if decrypted_vote is None:
        content = {
            "status": "failure",
            "message": "Invalid decryption - decrypted vote is none",
        }
        return content
    try:
        decrypted_vote["polling_place_id"] = polling_place_id
        decrypted_vote["_id"] = max_id + 1 + _id
    except Exception as e:
        content = {
            "status": "failure",
            "message": "Invalid decryption - unspecified",
        }

        print('--------------', e)

        return content
    content = {
        "status": "success",
        "message": "Decryption was successfully validated",
    }
    return content


async def validate_votes(request):
    DB = await get_database()

    polling_place_id = request.polling_place_id
    content = await validate_polling_place_id(polling_place_id)
    if content["status"] == "failure":
        return content

    key_pair = await DB.key_pairs.find_one({"polling_place_id": polling_place_id})

    if key_pair is None:
        content = {
            "status": "failure",
            "message": "Invalid private key for entered polling place id",
        }
        return content

    votes_to_be_inserted = []
    votes = request.votes
    max_id = await get_max_id("votes")

    tokens_to_be_validated = []

    for _id, encrypted_vote in enumerate(votes):
        private_key_pem = key_pair["private_key_pem"]
        g_public_key_pem = key_pair["g_public_key_pem"]

        decrypted_vote = electiersa.decrypt_vote(encrypted_vote, private_key_pem, g_public_key_pem)
        content = await validate_decryption(decrypted_vote, polling_place_id, max_id, _id)
        if content["status"] == "failure":
            return content
            
        decrypted_vote["polling_place_id"] = polling_place_id
        decrypted_vote["_id"] = max_id + 1 + _id

        content = await validate_party_and_candidates(decrypted_vote)
        if content["status"] == "failure":
            return content

        token = decrypted_vote["token"]
        content = await validate_token_with_polling_place_id(token, polling_place_id)
        if content["status"] == "failure":
            return content

        tokens_to_be_validated.append(token)

        election_id = decrypted_vote["election_id"]
        content = await validate_election_id(election_id)
        if content["status"] == "failure":
            return content

        votes_to_be_inserted.append(decrypted_vote)

    content = await validate_tokens(tokens_to_be_validated)
    if content["status"] == "failure":
        return content

    await DB.votes.insert_many(votes_to_be_inserted)

    content = {
        "status": "success",
        "message": "Vote was successfully precessed"
    }
    return content

@router.post("/vote", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}})
async def vote(request: schemas.VotesEncrypted):
    """
    Process candidate's vote
    """

    content = await validate_votes(request)
    if content["status"] == "failure":
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)
    return content

@router.get("/voting-data", response_model=schemas.VotingData, status_code=status.HTTP_200_OK)
async def get_voting_data():
    """
    Downlaod voting data json using command curl http://localhost:8222/elections/voting-data > config.json
    """
    DB = await get_database()

    polling_places = [polling_place async for polling_place in DB.polling_places.find()]
    parties_with_candidates = await get_parties_with_candidates()
    key_pairs = [key_pair async for key_pair in DB.key_pairs.find()]
    print(key_pairs)
    
    # -----
    # todo - toto musime potom vymazat, je to len pre ucel FASTAPI GUI
    # polling_places = polling_places[:2]
    # parties_with_candidates = parties_with_candidates[:2]
    # key_pairs = key_pairs[:2]
    # -----
    
    # multilingual text for VT application
    texts = {
        "elections_name_short": {
            "sk": "Voľby do NRSR",
            "en": "Parliamentary elections",
        },
        "elections_name_long": {
            "sk": "Voľby do národnej rady Slovenskej republiky",
            "en": "Parliamentary elections of Slovak Republic",
        },
        "election_date": {
            "sk": "30.11.2021",
            "en": "30.11.2021",
        }
    }
    
    image_paths = glob.glob("data/nrsr_2020/logos/*")
    for image_path in image_paths:
        for party_with_candidates in parties_with_candidates:
            image = image_path.split("/")[-1]
            if image == party_with_candidates["image"]:
                with open(image_path, "rb") as file:
                    image_bytes = base64.b64encode(file.read())
                    party_with_candidates["image_bytes"] = image_bytes

    content = {
        "polling_places": polling_places,
        "parties": parties_with_candidates,
        "key_pairs": key_pairs,
        "texts": texts
    }
    return content

# -----------------------------------------------------------------------------
from time import gmtime, strftime
from mdutils.mdutils import MdUtils

@router.get("/zapisnica", status_code=status.HTTP_200_OK)
async def get_zapisnica():
    polling_place_id = 0
    date = strftime("%d.%m.%Y %H:%M:%S", gmtime())
    print(date)

    DB = await get_database()

    parties = {}
    candidates = {}
    with open("src/server/routes/voting-data") as file:
        data = json.load(file)
        for party in data["parties"]:
            parties[party["_id"]] = party["name"]
            for candidate in party["candidates"]:
                candidates[candidate["_id"]] = candidate

    polling_place = data["polling_places"][polling_place_id]
    # print(polling_place)

    # Počer voličov zapísaných v zozname voličov
    registered_voters_count = polling_place["registered_voters_count"]
    print(registered_voters_count)

    # Počet voličov, ktorý sa zúčastnili na hlasovaní
    participated_voters_count = await DB.votes.count_documents({})
    print(participated_voters_count)

    # Účasť voličov vo voľbách v %
    voters_percentage = round((participated_voters_count / registered_voters_count) * 100, 2)
    print(voters_percentage)

    mdFile = MdUtils(file_name="zapisnica.md", title="XXX")

    # Počet získaných hlasov pre každú politickú stranu alebo hnutie
    mdFile.new_header(level=1, title='XXX')
    # mdFile.new_header(level=2, title="Počet získaných hlasov pre každú politickú stranu alebo koalíciu")
    # mdFile.new_line()


    list_of_strings = [
        "Číslo a názov politickej strany alebo koalície",
        "Počet získaných hlasov",
        "Podiel získaných hlasov v %"
    ]

    pipeline = [
        {"$group" : {"_id":"$party_id", "count":{"$sum":1}}},
        {"$sort":{"_id":1}}
    ]

    voted_parties = {}
    results = [result async for result in DB.votes.aggregate(pipeline)]
    for result in results:
        voted_parties[result["_id"]] = result["count"]

    print(len(parties))
    for party_id in parties:
        party_name = parties[party_id]
        party_number = party_id+1
        if party_id in voted_parties:
            party_votes_count = voted_parties[party_id]
        else:
            party_votes_count = 0

        party_votes_percentage = round((party_votes_count / registered_voters_count) * 100, 2)
        # print(party_number, party_name, party_votes_count, party_votes_percentage)

        list_of_strings.extend([
            f"{party_number} {party_name}",
            str(party_votes_count),
            str(party_votes_percentage)
        ])


    mdFile.new_line()
    mdFile.new_table(columns=3, rows=len(parties)+1, text=list_of_strings, text_align='left')


    pipeline = [
        {"$unwind": "$candidate_ids"},
        {"$group" : {"_id":"$candidate_ids", "count":{"$sum":1}}}
    ]

    voted_candidates = {}
    results = [result async for result in DB.votes.aggregate(pipeline)]
    for result in results:
        voted_candidates[result["_id"]] = result["count"]

    party_names = {}
    for candidate_id in candidates:
        candidate = candidates[candidate_id]

        if candidate_id in voted_candidates:
            candidate["votes_count"] = voted_candidates[candidate_id]
        else:
            candidate["votes_count"] = 0

        candidate_votes_percentage = round((candidate["votes_count"] / registered_voters_count) * 100, 2)
        candidate["votes_percentage"] = candidate_votes_percentage

        party_name = parties[candidates[candidate_id]["party_number"]-1]
        if party_name not in party_names:
            party_names[party_name] = [candidate]
        else:
            party_names[party_name].append(candidate)
    


    # Počet získaných hlasov pre každého kandidáta
    for party_name in party_names:
        candidates = party_names[party_name]
        party_number = candidates[0]["party_number"]

        # print(party_number)
        # print(party_name)
        # mdFile.new_header(level=2, title="Číslo a názov politickej strany alebo koalície")
        mdFile.new_header(level=2, title=f"{party_number} {party_name}")

        list_of_strings = [
            "Počet získaných hlasov",
            "Podiel získaných hlasov v %"
        ]

        for candidate in candidates:
            # print(candidate)

            list_of_strings.extend([
                str(candidate["votes_count"]),
                str(candidate["votes_percentage"]),
            ])

        mdFile.new_line()
        mdFile.new_table(columns=2, rows=len(candidates)+1, text=list_of_strings, text_align='left')
        break

    mdFile.create_md_file()
