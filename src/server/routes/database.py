# General modules
import json
from bson import Code
import traceback
import base64
import random
import string
from rsaelectie import rsaelectie

# Cryptography libraries
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# FastAPI modules
from fastapi import APIRouter, status
from starlette.responses import JSONResponse

# Server modules
from src.server import config
from src.server import schemas
from src.server.database import DB, get_parties_with_candidates


# Create FastAPI router
router = APIRouter(
    prefix = "/database",
    tags = ["Database"],
)


async def get_keys(collection_name: str):
    """
    Get all keys from provided collection. Helper function that emits all key inside collection using mapreduce. 
    """
    map = Code("function() { for (var key in this) { emit(key, null); } }")
    reduce = Code("function(key, stuff) { return null; }")
    result = await DB[collection_name].map_reduce(map, reduce, "myresults")
    return [key for key in await result.distinct('_id')]


@router.get("/schema", response_model=schemas.Collections, status_code=status.HTTP_200_OK, responses={500: {"model": schemas.Message}})
async def schema():
    """
    Get all collections from database
    """
    try:
        collections = []
        collection_names = [collection_name for collection_name in await DB.list_collection_names()]    
        for collection_name in collection_names:
            if collection_name != "myresults":
                collection_keys = await get_keys(collection_name)
                collections.append({
                    "name": collection_name,
                    "keys": collection_keys
                })
        
        content = {
            "collections": collections
        }
        return content
    
    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


async def load_json(path):
    """
    Helper to load json file
    """
    with open(path, encoding="utf8") as file:
        return json.load(file)


@router.post("/import-data", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={500: {"model": schemas.Message}})
async def import_data():
    try:
        DB.parties.drop()
        DB.candidates.drop()
        DB.polling_places.drop()
        DB.votes.drop()

        parties = await load_json(config.PARTIES_JSON)
        for party in parties:
            await DB.parties.insert_one(party)

        candidates = await load_json(config.CANDIDATES_JSON)
        for candidate in candidates:
            await DB.candidates.insert_one(candidate)

        polling_places = await load_json(config.POLLING_PLACES_JSON)
        for polling_place in polling_places:
            await DB.polling_places.insert_one(polling_place)

        content = {
            "status": "success",
            "message": "Data was successfully imported"
        }
        return content

    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


@router.post("/seed-data", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={500: {"model": schemas.Message}})
async def seed_data(number_of_votes: int):
    try:
        random.seed(config.SEED)

        DB.parties.drop()
        DB.candidates.drop()
        DB.polling_places.drop()
        DB.votes.drop()
        DB.key_pairs.drop()

        parties = await load_json(config.PARTIES_JSON)
        for idx, party in enumerate(parties):
            party["_id"] = str(idx)
            await DB.parties.insert_one(party)

        candidates = await load_json(config.CANDIDATES_JSON)
        for idx, candidate in enumerate(candidates):
            candidate["_id"] = str(idx)
            await DB.candidates.insert_one(candidate)

        polling_places = await load_json(config.POLLING_PLACES_JSON)
        for idx, polling_place in enumerate(polling_places):
            polling_place["_id"] = str(idx)
            await DB.polling_places.insert_one(polling_place)

        polling_places = [polling_place async for polling_place in DB.polling_places.find()]
        parties = await get_parties_with_candidates()

        votes_to_be_inserted = []
        for idx in range(number_of_votes):
            vote = {
                "_id": None,
                "polling_place_id": None,
                "data": {
                    "token": None,
                    "party_id": None,
                    "election_id": None,
                    "candidates_ids": []
                }
            }
            vote["_id"] = str(idx)

            selected_polling_place = random.choice(polling_places)
            vote["polling_place_id"] = selected_polling_place["_id"]

            selected_token = "".join([random.choice(string.ascii_lowercase + string.digits) for _ in range(10)])
            vote["data"]["token"] = selected_token

            selected_party = random.choice(parties)
            vote["data"]["party_id"] = selected_party["_id"]

            vote["data"]["election_id"] = config.ELECTION_ID

            selected_candidates = random.sample(selected_party["candidates"], random.randint(0,5))
            for selected_candidate in selected_candidates:
                vote["data"]["candidates_ids"].append(selected_candidate["_id"])

            votes_to_be_inserted.append(vote)

        await DB.votes.insert_many(votes_to_be_inserted)

        polling_place_id = [polling_place async for polling_place in DB.polling_places.find()][0]["_id"]

        private_key_pem, public_key_pem = await rsaelectie.get_rsa_key_pair(config.KEY_LENGTH)

        private_key_pem = private_key_pem.decode("utf-8")
        public_key_pem = public_key_pem.decode("utf-8")
        
        key_pair = {
            "polling_place_id": polling_place_id,
            "private_key_pem": private_key_pem,
            "public_key_pem": public_key_pem
        }
        await DB.key_pairs.insert_one(key_pair)

        content = {
            "status": "success",
            "message": "Test data was successfully seeded"
        }
        return content
        
    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)