import json
import glob
import base64
import string
import random
from pytest import yield_fixture

from electiersa import electiersa
from multiprocessing.sharedctypes import synchronized
import random
import string
import time
import os
from pprint import pprint

import traceback
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from src.server import config as c
from src.server import schemas
from src.server.database import DB, get_database
from src.server.database import get_parties_with_candidates, get_max_id
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
    candidates_ids = vote["candidates_ids"]

    if len(candidates_ids) > 5:
        content = {
            "status": "failure",
            "message": "Number of candidates is more than 5",
        }
        return content

    if len(set(candidates_ids)) != len(candidates_ids):
        content = {
            "status": "failure",
            "message": "Duplicate candidates ids",
        }
        return content

    parties = await get_parties_with_candidates()
    for party in parties:
        if party["_id"] == vote["party_id"]:
            candidate_match_count = 0
            for candidate in party["candidates"]:
                if candidate["_id"] in candidates_ids:
                    candidate_match_count += 1

            if candidate_match_count == len(candidates_ids):
                content = {
                    "status": "success",
                    "message": "Parties with candidates were successfully validated",
                }
                return content

            content = {
                "status": "failure",
                "message": "Invalid candidates ids",
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
            "message": "Invalid decryption",
        }
        return content
    try:
        decrypted_vote["polling_place_id"] = polling_place_id
        decrypted_vote["_id"] = max_id + 1 + _id
    except:
        content = {
            "status": "failure",
            "message": "Invalid decryption",
        }
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
    DB = await get_database()

    polling_places = [polling_place async for polling_place in DB.polling_places.find()]
    parties_with_candidates = await get_parties_with_candidates()
    key_pairs = [key_pair async for key_pair in DB.key_pairs.find()]
    print(key_pairs)
    
    # -----
    # todo - toto musime potom vymazat, je to len pre ucel FASTAPI GUI
    polling_places = polling_places[:2]
    parties_with_candidates = parties_with_candidates[:2]
    key_pairs = key_pairs[:2]
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

# helper function for bulk import, inserts index name into object,
def bulk_insert_documents(index, data):

    start_time = time.time()
    count = len(data)
    
    for row in data:
        row["_index"] = index

    res = helpers.bulk(ES, data)
    print(f"Inserted {count} documents. Took {round(time.time() - start_time,3)} s")
    return res

# TODO add request schema
@router.post("/setup-elastic-vote-index", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def setup_elastic_votes_index():
    
    if not ES.ping():
        raise ValueError("Connection to ES failed")

    content = {
        "status": "success",
        "message": f"ES index setup success"
    }
    return content

# TODO run as cron
# TODO add request schema
# TODO database transaction (ATOMIC)
# TODO insertovanie cisla id pre vote nech neni od 1 ale object random id
# TODO spravit menej dopytov najlepsie 1

@router.post("/synchronize-votes-es", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def synchronize_votes_ES():

    if not ES.ping():
        raise ValueError("Connection to ES failed")

    DB  = await get_database()

    # get bulk votes that are not synced
    unsynced_votes = [vote async for vote in DB.votes.aggregate([
        { '$match': {
            'synchronized': None
        }
        }, {
            '$limit': c.ES_SYNCHRONIZATION_BATCH_SIZE
        }
    ])]

    # insert them to ES
    data = []
    for vote in unsynced_votes:

        polling_place_id = vote["polling_place_id"]

        candidates = []
        for candidate_id in vote["candidates_ids"]:

            candidate_data = await DB.candidates.find_one({"_id": candidate_id})

            name = f'{candidate_data["first_name"]} {candidate_data["last_name"]}'
            name = candidate_data["degrees_before"] + " " + name if len(candidate_data["degrees_before"]) else name
            candidates.append({
                "id" : str(candidate_id),
                "fullname" : name,
                "number" : int(candidate_data["order"])
            })

        
        party_data = await DB.parties.find_one({"_id": vote["party_id"]})
        polling_place_data = await DB.polling_places.find_one({"_id": polling_place_id})

        vote_data = {   
            "id" : str(vote["_id"]),
            "token" : vote["token"],
            "election_id": vote["election_id"],
            "date" : int(time.time()),
            "party" : {
                "id" : str(vote["party_id"]),
                "name" : party_data["name"]
            },
            "polling_place": {
                "id" : str(polling_place_id),
                "municipality_name" : polling_place_data["municipality_name"],
                "administrative_area_name": polling_place_data["administrative_area_name"],
                "county_name" : polling_place_data["county_name"],
                "region_name" : polling_place_data["region_name"]
            },
            "candidates": candidates
        }
        data.append(vote_data)

    if len(data):    
        bulk_insert_documents("votes", data)

        # update synced votes state
        unsynced_votes_ids = [ vote["_id"] for vote in unsynced_votes]
        await DB.votes.update_many(
            { 
                "_id" : {
                    "$in" : unsynced_votes_ids
                }
            },
            { "$set": { "synchronized": True }},
        )

    content = {
        "status": "success",
        "message": f"{len(data)} votes were successfully synchronized"
    }

    return content
    # TODO check if inserted correctly
