import json
import glob
import base64
import random
import string
import random

import traceback
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from src.server import config
from src.server import schemas
from src.server.database import DB

# Create FastAPI router
router = APIRouter(
    prefix = "/elections",
    tags = ["Elections"],
)

KEY_PAIRS = None
PARTIES_WITH_CANDIDATES = None

async def save_json(data, path):
    with open(f"{path}.json", "w", encoding="utf8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


async def get_parties_with_candidates():
    pipeline = [{
        "$lookup": {
            "from": "candidates",
            "localField": "party_number",
            "foreignField": "party_number",
            "as": "candidates"
        }
    }]
    result = [doc async for doc in DB.parties.aggregate(pipeline)]
    return result


async def validate_polling_place_id(polling_place_id):
    global KEY_PAIRS

    if not any([key_pair["polling_place_id"] == polling_place_id for key_pair in KEY_PAIRS]):
        return False
    return True


async def validate_token(token, tokens):
    if token in tokens:
        return False
    return True


async def validate_party_and_candidates(data):
    candidates_ids = data["candidates_ids"]

    if len(candidates_ids) > 5:
        return False

    if len(list(set(candidates_ids))) != len(candidates_ids):
        return False

    parties = await get_parties_with_candidates()
    for party in parties:
        if str(party["_id"]) == data["party_id"]:
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
    global KEY_PAIRS, PARTIES_WITH_CANDIDATES
    
    if not KEY_PAIRS:
        KEY_PAIRS = [key_pair async for key_pair in DB.key_pairs.find()]

    if not PARTIES_WITH_CANDIDATES:
        PARTIES_WITH_CANDIDATES = get_parties_with_candidates()

    tokens_to_be_inserted_into_db = []
    votes = request.votes
    for vote in votes:
        vote = dict(vote)
        vote["data"] = dict(vote["data"])

        polling_place_id = vote["polling_place_id"]
        if not await validate_polling_place_id(polling_place_id):
            return False

        # try to decipher data with the private key somehow
        # vysledok nech je dictionary data, ktory pouzivame nizsie

        data = vote["data"]
        if not await validate_party_and_candidates(data):
            return False

        token = data["token"]
        tokens = [vote["data"]["token"] async for vote in DB.votes.find()]
        if not await validate_token(token, tokens):
            return False
        else:
            tokens_to_be_inserted_into_db.append({
                "token": token
            })

        election_id = data["election_id"]
        if not await validate_election_id(election_id):
            return False

    await DB.tokens.insert_many(tokens_to_be_inserted_into_db)
    
    return True


@router.post("/vote", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def vote(request: schemas.Votes):
    """
    Process candidate's vote
    """

    try:
        if not await validate_votes(request):
            content = {
                "status": "failure",
                "message": "Vote was not processed"
            }
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)            

        votes = request.votes
        for vote in votes:
            vote = dict(vote)
            vote["data"] = dict(vote["data"])
            await DB.votes.insert_one(vote)

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


@router.post("/seed/votes/{number}", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={500: {"model": schemas.Message}})
async def seed_votes(number: int):
    """
    Immitate voting process
    """

    try:
        parties = await get_parties_with_candidates()

        data = []
        for _ in range(number):
            selected_party = random.choice(parties)

            # token zatial len provizorne, toto nam bude posielat G
            token = "".join([random.choice(string.ascii_uppercase + string.digits) for _ in range(10)])

            vote = {
                "polling_place_id": "todo",
                "data": {
                    "token": token,
                    "party_id": selected_party["_id"],
                    "election_id": "todo",
                    "candidates_ids": []
                }
            }

            selected_candidates = random.sample(selected_party["candidates"], 5)
            for selected_candidate in selected_candidates:
                vote["data"]["candidates_ids"].append(selected_candidate["_id"])

            data.append(vote)
        
        DB.votes.insert_many(data)

        content = {
            "status": "success",
            "message": "Votes were successfully seeded"
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
        # parties with aggregate candidates
        parties = await get_parties_with_candidates()
        
        # -----
        # todo - toto musime potom vymazat, je to len pre ucel FASTAPI GUI
        parties = parties[:2]
        # -----

        for party in parties:
            party["_id"] = str(party["_id"])
            for candidate in party["candidates"]:
                candidate["_id"] = str(candidate["_id"])
        
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
            for party in parties:
                image = image_path.split("/")[-1]
                if image == party["image"]:
                    with open(image_path, "rb") as file:
                        image_bytes = base64.b64encode(file.read())
                        party["image_bytes"] = image_bytes

        # combine all the data together
        data = {
            "parties": parties,
            "texts": texts
        }
        return data
    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)
