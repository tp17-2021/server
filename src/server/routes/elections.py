import json
import glob
import base64
import string
import random
from pytest import yield_fixture

from rsaelectie import rsaelectie

import traceback
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from src.server import config
from src.server import schemas
from src.server.database import DB, get_database
from src.server.database import get_parties_with_candidates, get_max_id
import asyncio

# Create FastAPI router
router = APIRouter(
    prefix = "/elections",
    tags = ["Elections"],
)


async def validate_polling_place_id(polling_place_id):
    DB  = await get_database()

    if await DB.key_pairs.find_one({"polling_place_id":polling_place_id}) is None:
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

    if len(list(set(candidates_ids))) != len(candidates_ids):
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


async def validate_token(token):
    DB = await get_database()

    if await DB.votes.find_one({"token":token}) is not None:
        content = {
            "status": "failure",
            "message": "Invalid token",
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


async def validate_votes(request):
    DB = await get_database()

    polling_place_id = request.polling_place_id
    content = await validate_polling_place_id(polling_place_id)
    if content["status"] == "failure":
        return content

    votes_to_be_inserted = []
    encrypted_votes = request.votes
    key_pairs = [key_pair async for key_pair in DB.key_pairs.find({}, {"polling_place_id":1, "private_key_pem":1, "_id":0})]
    max_id = await get_max_id("votes")
    
    for _id, encrypted_vote in enumerate(encrypted_votes):
        match = False
        for key_pair in key_pairs:
            if key_pair["polling_place_id"] == polling_place_id:
                private_key_pem = key_pair["private_key_pem"]
                decrypted_vote = await rsaelectie.decrypt_vote(private_key_pem, encrypted_vote)
                decrypted_vote["polling_place_id"] = polling_place_id
                decrypted_vote["_id"] = max_id + 1 + _id

                match = True
                break

        if not match:
            content = {
                "status": "failure",
                "message": "Invalid private key for entered polling place id",
            }
            return content

        content = await validate_party_and_candidates(decrypted_vote)
        if content["status"] == "failure":
            return content

        token = decrypted_vote["token"]
        content = await validate_token(token)
        if content["status"] == "failure":
            return content

        election_id = decrypted_vote["election_id"]
        content = await validate_election_id(election_id)
        if content["status"] == "failure":
            return content

        votes_to_be_inserted.append(decrypted_vote)

    await DB.votes.insert_many(votes_to_be_inserted)

    content = {
        "status": "success",
        "message": "Vote was successfully precessed"
    }
    return content


@router.post("/vote", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def vote(request: schemas.VotesEncrypted):
    """
    Process candidate's vote
    """

    try:
        content = await validate_votes(request)
        if content["status"] == "failure":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)
        return content

    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


@router.get("/voting-data", response_model=schemas.VotingData, status_code=status.HTTP_200_OK, responses={500: {"model": schemas.Message}})
async def get_voting_data():
    try:
        parties_with_candidates = await get_parties_with_candidates()
        
        # -----
        # todo - toto musime potom vymazat, je to len pre ucel FASTAPI GUI
        parties_with_candidates = parties_with_candidates[:2]
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
            "parties": parties_with_candidates,
            "texts": texts
        }
        return content
    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)
