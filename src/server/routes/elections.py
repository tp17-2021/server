import json
import glob
import base64
import string
import random

from rsaelectie import rsaelectie

import traceback
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from src.server import config
from src.server import schemas
from src.server.database import DB
from src.server.database import get_parties_with_candidates, get_max_id
from src.server.routes.encryption import encrypt_message

# Create FastAPI router
router = APIRouter(
    prefix = "/elections",
    tags = ["Elections"],
)


async def save_json(data, path):
    with open(f"{path}.json", "w", encoding="utf8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def validate_polling_place_id(polling_place_id):
    if not any([key_pair["polling_place_id"] == polling_place_id async for key_pair in DB.key_pairs.find()]):
        return False
    return True


async def validate_token(token):
    tokens = [vote["token"] async for vote in DB.votes.find()]
    if token in tokens:
        return False
    return True


async def validate_party_and_candidates(vote):
    candidates_ids = vote["candidates_ids"]

    if len(candidates_ids) > 5:
        return False

    if len(list(set(candidates_ids))) != len(candidates_ids):
        return False

    parties = await get_parties_with_candidates()
    for party in parties:
        if str(party["_id"]) == vote["party_id"]:
            candidate_match_count = 0
            for candidate in party["candidates"]:
                if str(candidate["_id"]) in candidates_ids:
                    candidate_match_count += 1

            if candidate_match_count == len(candidates_ids):
                return True
            return False
    return False


async def validate_election_id(election_id):
    if election_id != config.ELECTION_ID:
        return False
    return True


async def validate_votes(request):
    votes_to_be_inserted = []

    polling_place_id = request.polling_place_id
    if not await validate_polling_place_id(polling_place_id):
        return False

    key_pairs = [key_pair async for key_pair in DB.key_pairs.find()]

    max_id = await get_max_id("votes")

    encrypted_votes = request.votes
    for idx, encrypted_vote in enumerate(encrypted_votes):
        match = False
        for key_pair in key_pairs:
            if key_pair["polling_place_id"] == polling_place_id:
                private_key_pem = key_pair["private_key_pem"]
                decrypted_vote = await rsaelectie.decrypt_vote(private_key_pem, encrypted_vote)
                decrypted_vote["polling_place_id"] = polling_place_id
                decrypted_vote["_id"] = max_id + 1 + idx

                match = True
                break

        if not match:
            return False

        if not await validate_party_and_candidates(decrypted_vote):
            return False

        token = decrypted_vote["token"]
        if not await validate_token(token):
            return False

        election_id = decrypted_vote["election_id"]
        if not await validate_election_id(election_id):
            return False

        votes_to_be_inserted.append(decrypted_vote)

    return votes_to_be_inserted


@router.post("/vote", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def vote(request: schemas.VotesEncrypted):
    """
    Process candidate's vote
    """

    try:
        votes_to_be_inserted = await validate_votes(request)
        if not votes_to_be_inserted:
            content = {
                "status": "failure",
                "message": "Votes were not processed"
            }
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)            
        
        for vote_to_be_inserted in votes_to_be_inserted:
            await DB.votes.insert_one(vote_to_be_inserted)

        content = {
            "status": "success",
            "message": "Vote was successfully precessed"
        }
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
