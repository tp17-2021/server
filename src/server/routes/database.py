# General modules
import json
from bson import Code
import traceback
import base64
import random
import string

from electiersa import electiersa


# Cryptography libraries
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# FastAPI modules
from fastapi import APIRouter, status
from starlette.responses import JSONResponse

# Server modules
from src.server import config
from src.server import schemas
from src.server.database import get_database, get_parties_with_candidates


# Create FastAPI router
router = APIRouter(
    prefix = "/database",
    tags = ["Database"],
)


async def get_keys(collection_name: str):
    """
    Get all keys from provided collection. Helper function that emits all key
    inside collection using mapreduce. 
    """
    DB  = await get_database()

    map = Code("function() { for (var key in this) { emit(key, null); } }")
    reduce = Code("function(key, stuff) { return null; }")
    result = await DB[collection_name].map_reduce(map, reduce, "myresults")
    return [key for key in await result.distinct('_id')]


@router.get("/schema", response_model=schemas.Collections, status_code=status.HTTP_200_OK)
async def schema():
    """
    Get all collections from database
    """
    DB  = await get_database()
    
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

async def load_json(path):
    """
    Helper to load json file
    """
    with open(path, encoding="utf8") as file:
        return json.load(file)


@router.post("/import-data", response_model=schemas.Message, status_code=status.HTTP_200_OK)
async def import_data():
    DB  = await get_database()
    
    DB.parties.drop()
    DB.candidates.drop()
    DB.polling_places.drop()
    DB.votes.drop()

    parties = await load_json(config.PARTIES_JSON)
    for _id, party in enumerate(parties):
        party["_id"] = _id
        await DB.parties.insert_one(party)

    candidates = await load_json(config.CANDIDATES_JSON)
    for _id, candidate in enumerate(candidates):
        candidate["_id"] = _id
        await DB.candidates.insert_one(candidate)

    polling_places = await load_json(config.POLLING_PLACES_JSON)
    for _id, polling_place in enumerate(polling_places):
        polling_place["_id"] = _id
        await DB.polling_places.insert_one(polling_place)

    content = {
        "status": "success",
        "message": "Data was successfully imported"
    }
    return content


async def generate_token():
    random.seed(config.SEED)
    token = "".join([random.choice(string.ascii_lowercase + string.digits) for _ in range(10)])
    return token

async def choose_candidates(candidates):
    random.seed(config.SEED)
    candidates = random.sample(candidates, random.randint(0,5))
    return candidates


@router.post("/seed-data", response_model=schemas.Message, status_code=status.HTTP_200_OK)
async def seed_data(number_of_votes: int):
    DB  = await get_database()

    random.seed(config.SEED)

    DB.parties.drop()
    DB.candidates.drop()
    DB.polling_places.drop()
    DB.votes.drop()
    DB.key_pairs.drop()

    parties = await load_json(config.PARTIES_JSON)
    for _id, party in enumerate(parties):
        party["_id"] = _id
        await DB.parties.insert_one(party)

    candidates = await load_json(config.CANDIDATES_JSON)
    for _id, candidate in enumerate(candidates):
        candidate["_id"] = _id
        await DB.candidates.insert_one(candidate)

    polling_places = await load_json(config.POLLING_PLACES_JSON)
    for _id, polling_place in enumerate(polling_places):
        polling_place["_id"] = _id
        await DB.polling_places.insert_one(polling_place)

    polling_places = [polling_place async for polling_place in DB.polling_places.find()]
    parties = await get_parties_with_candidates()

    votes_to_be_inserted = []
    for _id in range(number_of_votes):
        vote = {
            "_id": None,
            "token": None,
            "party_id": None,
            "election_id": None,
            "candidates_ids": [],
            "polling_place_id": None
        }
        vote["_id"] = _id

        selected_polling_place = random.choice(polling_places)
        vote["polling_place_id"] = selected_polling_place["_id"]

        selected_token = await generate_token()
        vote["token"] = selected_token

        selected_party = random.choice(parties)
        vote["party_id"] = selected_party["_id"]

        vote["election_id"] = config.ELECTION_ID

        selected_candidates = await choose_candidates(selected_party["candidates"])
        for selected_candidate in selected_candidates:
            vote["candidates_ids"].append(selected_candidate["_id"])

        votes_to_be_inserted.append(vote)

    await DB.votes.insert_many(votes_to_be_inserted)

    # key pair for polling_place_id = 0
    polling_place_id = 0

    private_key_pem = "-----BEGIN RSA PRIVATE KEY-----\n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\n-----END RSA PRIVATE KEY-----"
    public_key_pem = "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAtbRRyrioFx4NuRYbh3pN\nU/p8CRSQqxd+VV45YEY12n7JKUim99wdUdKxePIRmw3rmFF7eyBOjddwycxSZ24I\ngiJXyETRh4zF4QF1iVKFNvkbJwHIXy6fy+WokVG1AwJtFqjPvEzTVFgUkJavYHGv\nw7otVLZT+2cSBAytNUhwQjTq+v76ktwRu3FV466QDo/DxijLwpMMf6TDQvhEi61m\nykrsJB3Wgn+/fueqUIVhxUffTwVXC0qyEfJ3LmSuxc+Z/GKYYUun8eKxmq9xBJUr\nRl+BJOYGQ5/pTQQD7RltZj7pgw6o4kXtalGmk7ya1v5ghoHXwGhGJv12cODJLsje\nxl922oYz2XCXgiwxiyckIRccLfBNsA3U+nE31lW+qPZyz2heJBLLJpL3v/A9xeBU\n9nXEsJ/bfsmEaOlK0Z0w+a3IKGaAVCFrIRCBdviEEdD79JiFG9c1hlG0+znCVSVD\nmxJmh3wngm6WwIH3mGUuYUrApewyl93fJqMuLVcVA2ARfS//FPWHAIkD0vT94b47\n6DAqyboC72jDsqWDdSW66mZLaFfI9djX//MdVAp3T8MMbRU/h2uX5kVQC2Au8tGH\nZnL6uVVC66tVHAgErH+sgsrQpqKBokmb7dPqFOF4ORz/kdi+JHX7edpn3GKGRehJ\nA621Hjd92Wezgt5MtNzoeW0CAwEAAQ==\n-----END PUBLIC KEY-----"

    key_pair = {
        "_id": 0,
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
    