from asyncore import poll
import re
from mdutils.mdutils import MdUtils
from time import gmtime, strftime
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
ES = Elasticsearch(hosts=[{"scheme": "http", 'host': os.environ['ELASTIC_HOST'], 'port': int(
    os.environ['ELASTIC_PORT'])}])

# Create FastAPI router
router = APIRouter(
    prefix="/elections",
    tags=["Elections"],
)


async def validate_polling_place_id(polling_place_id):
    DB = await get_database()

    if await DB.key_pairs.count_documents({"polling_place_id": polling_place_id}) == 0:
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

    if vote["party_id"] is None:

        if len(candidate_ids) != 0:
            content = {
                "status": "failure",
                "message": "When party_id is None there is no possibility to have length of candidate_ids greater than zero",
            }
        else:
            content = {
                "status": "success",
                "message": "Parties with candidates were successfully validated",
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

    if await DB.votes.count_documents({"token": token, "polling_place_id": polling_place_id}) != 0:
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

        decrypted_vote = electiersa.decrypt_vote(
            encrypted_vote, private_key_pem, g_public_key_pem)
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


async def get_config_file(mode="all", polling_place_id=None):
    DB = await get_database()

    polling_place = None
    polling_places = None

    if mode == "gateway" and polling_place_id is not None:
        polling_place = await DB.polling_places.find_one({"_id": polling_place_id}, {"_id": 0})

    if mode == "all":
        polling_places = [polling_place async for polling_place in DB.polling_places.find()]

    print(polling_place, polling_places, flush=True)
    parties_with_candidates = await get_parties_with_candidates()
    key_pairs = [key_pair async for key_pair in DB.key_pairs.find()]

    regions = [polling_place async for polling_place in DB.polling_places.aggregate([
        {
            '$group': {
                '_id': '$region_code',
                'name': {
                    '$first': '$region_name'
                }
            }
        },
        {
            '$sort': {
                '_id': 1
            }
        },
        {
            '$project': {
                'code': '$_id',
                'name': '$name',
                '_id': 0
            }
        }
    ])]

    counties = [polling_place async for polling_place in DB.polling_places.aggregate([
        {
            '$group': {
                '_id': '$county_code',
                'name': {
                    '$first': '$county_name'
                },
                'region_code': {
                    '$first': '$region_code'
                }
            }
        },
        {
            '$sort': {
                '_id': 1
            }
        },
        {
            '$project': {
                'code': '$_id',
                'name': '$name',
                'region_code' : '$region_code',
                '_id': 0
            }
        }
    ])]

    municipalitites = [polling_place async for polling_place in DB.polling_places.aggregate([
        {
            '$group': {
                '_id': '$municipality_code',
                'name': {
                    '$first': '$municipality_name'
                },
                'region_code': {
                    '$first': '$region_code'
                },
                'county_code': {
                    '$first': '$county_code'
                }
            }
        },
        {
            '$sort': {
                'name': 1
            }
        }, {
            '$project': {
                'code': '$_id',
                'name': '$name',
                'region_code' : '$region_code',
                'county_code' : '$county_code',
                '_id': 0
            }
        }
    ])]

    # print(key_pairs)

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
        },
        "contact": {
            "title": {
                "sk": "Volebná centrála Bratislava",
                "en": "Volebná centrála Bratislava"
            },
            "contact_person": "Jožko Mrkvička",
            "address": "Volebná 1, 853 01 Bratislava",
            "phone": "+421 910 123 456",
            "email": "support@volby.sk"
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

    if mode == 'gateway':
        return {
            "polling_place": polling_place,
            "parties": parties_with_candidates,
            "key_pairs": key_pairs,
            "texts": texts
        }
    else:
        return {
            # "polling_places": polling_places,
            "parties": parties_with_candidates,
            "key_pairs": key_pairs,
            "texts": texts,
            "regions": regions,
            "counties": counties,
            "municipalities": municipalitites
        }

# @router.get("/voting-data", response_model=schemas.VotingData, status_code=status.HTTP_200_OK)
@router.get("/voting-data", status_code=status.HTTP_200_OK)
async def get_voting_data():
    """
    Download voting data json (used on statistics FE) using command curl http://localhost:8222/elections/voting-data > config.json
    """
    content = await get_config_file()
    return content


@router.get("/gateway-config", status_code=status.HTTP_200_OK)
async def get_gateway_config(polling_place_id: int):
    """
    Download gateway config data json using command curl http://localhost:8222/elections/gateway-config > config.json
    """

    content = await get_config_file(
        mode="gateway", polling_place_id=polling_place_id)
    return content


def replace_header_polling_place(region_code: int, county_code: int, municipality_code: int, polling_place_code: int) -> str:
    with open("src/server/routes/table_polling_place.html", "r", encoding="utf-8") as file:
        text = file.read()
        text = re.sub(r"region_code", str(region_code), text)
        text = re.sub(r"county_code", str(county_code), text)
        text = re.sub(r"municipality_code", str(municipality_code), text)
        text = re.sub(r"polling_place_code", str(polling_place_code), text)
        return text


def replace_header_parties(parties) -> str:
    table_rows = []
    for party in parties:
        tr = f'<tr><td><div style="width: 80px">{party["order"]}</div></td><td style="text-align:left"><div style="width: 420px">{party["name"]}</div></td><td><div style="width: 75px">{party["votes_count"]}</div></td><td><div style="width: 90px">{format(float(party["votes_percentage"]), ".2f")}</div></td></tr>'
        table_rows.append(tr)

    with open("src/server/routes/table_parties.html", "r", encoding="utf-8") as file:
        text = file.read()
        text = re.sub(r"table_rows", "".join(table_rows), text)
        return text


def load_config(polling_place_id: int):
    parties = {}
    candidates = {}
    with open("src/server/routes/voting-data") as file:
        data = json.load(file)
        for party in data["parties"]:
            parties[party["_id"]] = party["name"]
            for candidate in party["candidates"]:
                candidates[candidate["_id"]] = candidate

    return parties, candidates, data["polling_places"][polling_place_id]


async def get_party_votes(parties, polling_place):
    DB = await get_database()

    pipeline = [
        {"$group": {"_id": "$party_id", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]

    voted_parties = {}
    results = [result async for result in DB.votes.aggregate(pipeline)]
    for result in results:
        voted_parties[result["_id"]] = result["count"]

    parties_tmp = parties.copy()
    for party_id in parties_tmp:
        if party_id in voted_parties:
            votes_count = voted_parties[party_id]
        else:
            votes_count = 0

        parties_tmp[party_id] += f"\t{votes_count}"

        registered_voters_count = polling_place["registered_voters_count"]
        votes_percentage = round(
            (votes_count / registered_voters_count) * 100, 2)
        parties_tmp[party_id] += f"\t{votes_percentage}"

    return parties_tmp


async def get_candidate_votes(parties, candidates, polling_place):
    DB = await get_database()

    pipeline = [
        {"$unwind": "$candidate_ids"},
        {"$group": {"_id": "$candidate_ids", "count": {"$sum": 1}}}
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

        registered_voters_count = polling_place["registered_voters_count"]
        candidate_votes_percentage = round(
            (candidate["votes_count"] / registered_voters_count) * 100, 2)
        candidate["votes_percentage"] = candidate_votes_percentage

        party_name = parties[candidates[candidate_id]["party_number"]-1]
        if party_name not in party_names:
            party_names[party_name] = [candidate]
        else:
            party_names[party_name].append(candidate)

    return party_names


def replace_header_candidates(candidates) -> str:
    table_rows = []
    for candidate in candidates:
        tr = f'<tr><td><div style="width: 80px">{candidate["order"]}</div></td><td style="text-align:left"><div style="width: 420px">{candidate["name"]}</div></td><td><div style="width: 75px">{candidate["votes_count"]}</div></td><td><div style="width: 90px">{format(candidate["votes_percentage"], ".2f")}</div></td></tr>'
        table_rows.append(tr)

    with open("src/server/routes/table_candidates.html", "r", encoding="utf-8") as file:
        text = file.read()
        text = re.sub(r"table_rows", "".join(table_rows), text)
        return text


def replace_header_president(president) -> str:
    table_row = f'<tr><td style="text-align:left">{president.name}</td><td>{"áno" if president.agree else "nie"}</td></tr>'

    with open("src/server/routes/table_president.html", "r", encoding="utf-8") as file:
        text = file.read()
        text = re.sub(r"table_row", table_row, text)
        return text


def replace_header_members(members) -> str:
    table_rows = []
    for member in members:
        tr = f'<tr><td style="text-align:left">{member.name}</td><td>{"áno" if member.agree else "nie"}</td></tr>'
        table_rows.append(tr)

    with open("src/server/routes/table_members.html", "r", encoding="utf-8") as file:
        text = file.read()
        text = re.sub(r"table_rows", "".join(table_rows), text)
        return text


@router.post("/zapisnica", status_code=status.HTTP_200_OK)
async def get_zapisnica(request: schemas.Commission):
    DB = await get_database()

    polling_place_id = request.polling_place_id
    parties, candidates, polling_place = load_config(polling_place_id)

    date = time.strftime("%d.%m.%Y")
    date_and_time = time.strftime("%d.%m.%Y %H:%M:%S")
    registered_voters_count = polling_place["registered_voters_count"]
    participated_voters_count = await DB.votes.count_documents({})
    participated_voters_percentage = round(
        participated_voters_count / registered_voters_count, 2)

    table_polling_place = replace_header_polling_place(str(polling_place["region_code"]), str(
        polling_place["county_code"]), str(polling_place["municipality_code"]), str(polling_place["polling_place_number"]))

    data = []
    result = await get_party_votes(parties, polling_place)
    for party_id in result:
        name, votes_count, votes_percentage = result[party_id].split("\t")
        data.append({
            "order": party_id+1,
            "name": name,
            "votes_count": votes_count,
            "votes_percentage": votes_percentage
        })
    table_parties = replace_header_parties(data)

    table_candidates = ""
    result = await get_candidate_votes(parties, candidates, polling_place)
    for party_name in result:
        table_candidates += f"### {party_name}\n"

        data = []
        C = result[party_name]
        for c in C:
            candidate_name = f"{c['first_name']} {c['last_name']}"
            if len(c["degrees_before"]):
                candidate_name += f", {c['degrees_before']}"

            data.append({
                "order": c["order"],
                "name": candidate_name,
                "votes_count": c["votes_count"],
                "votes_percentage": c["votes_percentage"],
            })

        c = replace_header_candidates(data)
        table_candidates += f"{c}\n"
        break  # delete this line when done

    table_president = replace_header_president(request.president)
    table_members = replace_header_members(request.participated_members)

    print("OK")

    with open("src/server/routes/template.md", "r", encoding="utf-8") as file:
        text = file.read()
        text = re.sub(r"REGISTERED_VOTERS_COUNT",
                      str(registered_voters_count), text)
        text = re.sub(r"PARTICIPATED_VOTERS_COUNT",
                      str(participated_voters_count), text)
        text = re.sub(r"PARTICIPATED_VOTERS_PERCENTAGE", format(
            participated_voters_percentage, ".2f"), text)
        text = re.sub(r"TABLE_POLLING_PLACE", table_polling_place, text)
        text = re.sub(r"TABLE_PARTIES", table_parties, text)
        text = re.sub(r"TABLE_CANDIDATES", table_candidates, text)
        text = re.sub(r"PARTICIPATED_MEMBERS_COUNT", str(
            len(request.participated_members)+1), text)
        text = re.sub(r"TABLE_PRESIDENT", table_president, text)
        text = re.sub(r"TABLE_MEMBERS", table_members, text)
        text = re.sub(r"DATE_AND_TIME", date_and_time, text)
        text = re.sub(r"DATE", date, text)

    with open("src/server/routes/output.md", "w", encoding="utf-8") as file:
        file.write(text)
