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

    private_key_pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAs6lvNfr+Eo6Mt+mW95fhjUbCRygCNok8Y8yIu502lpDiz3bN\ndR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7IEpRSmY1nElabMoBbU2vsPWBsu7WR\n31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPuRVtuHy/q2tD5sY2ekWJc1YsoeQ5J\nDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c2P4NpNgSJ2NT8aF/bDbu3sQk9QuQ\nXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchqrYj5Xnql/wcrnyOhcgeKsOBieH/f\nETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG47QIDAQABAoIBAAEotU5QfGpm8gUF\n/64cOMs1Bm/4E+QmCFrF5IQ1VFvlBBmQGZGko6i6AHR0CtCN2OuVAne9sTtfYyjU\nLvPdzUcMQ3q40+B3n5BB6UvFZ2SIiu1RE3nDCRyFx/VWATEqwZKTmaEUsO1BMHwx\nJWW5+K4tb1HunUZ20M2OEfkps39438Vk1R4I/kJqhp8E7mLYshBHyK1OwOgiInE4\n1Z2SwAhvGKnNE3TnBlV7/K5XFQg3b7QWORHvlvnNHU7ed8TXmizp7No6Qxl1ZJ2z\nier3f+XiMAryIb7AyBJyIWGnQllrDhff5hhNObltLmmaAkQm3LSsJ52GU9e4i/6c\nF/sshLECgYEAu78IM4Sj3D+wd6lMNVInU7Np8o8L5Ihq9Y1ccHmyvbVdxeGPIfKo\n/j/WwoCQJPKFQJLjQru3s1nVOOYNE5/CUQEEeFguzRL43UtzywONc1+L4a2MOnqO\n8ywQF1OrxByFy9eFLdN5ETdDhriajx8VM0hRrmeLsiGcmVZet1lFjjkCgYEA9PoD\n3x2qaCrTe3mZPHzfayHYWVFFxvRYOjxmIbOdzQZPeQA1tXEHyHnY/z3ibA+v3iQu\nQ2n5RQM4/+ItjS2xrwL+hlU3yue67HfBuUyFcFjhEUu0sdN4439d3K9hAeX7eTfB\nZ2CsNieqPxYZj6tSL4+0Fru4o4VpD79u7pSlgFUCgYAdWiJoG4aauoJWUuuNMojf\ndx9LQr3zPriqJy2akAw3yJEejMMZ5ZwyE7z5r6vZeukGTXCmUD7KFXNWb/D/bmys\nyWHvhqnaeerafh9eT/HfZcKyx7Uyt1J+BheF7hjeki8AzXMO1Q8Kd/9gop/XXF6u\nI9JRV/LpKIQZHP214IkVUQKBgQCpqO09fIIkGmTUwuZJagIhZBM96Hd2zoq76lCh\nTpAfChvIJUkNG/bT9O8/9k/1nveh1VTlA2PLU+wJ606408iW+G/mAObe85YVZusX\ntdNEd4mIPPIrpdW3WOJckGmSswBydxbOzbj22Imjn16cjX4hylhi1ieNuDuG2IGv\nYess8QKBgQCrT1ATnUxqacw/x8RRJpZWV4rnrkujA2XPLu4YaMODzVSkk+HVEabH\nJtA4AV6O0bneAgywBltg9wL0L98Q6ckuEo6hA9rskvwxQAk9uawJDzy1Bq/aEcSD\nu707LpYyMboRA/+1Sw8GEYF1iKdVJnGN1pjse4V4mJvobPPEZ+4Atw==\n-----END RSA PRIVATE KEY-----"
    public_key_pem = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs6lvNfr+Eo6Mt+mW95fh\njUbCRygCNok8Y8yIu502lpDiz3bNdR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7I\nEpRSmY1nElabMoBbU2vsPWBsu7WR31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPu\nRVtuHy/q2tD5sY2ekWJc1YsoeQ5JDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c\n2P4NpNgSJ2NT8aF/bDbu3sQk9QuQXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchq\nrYj5Xnql/wcrnyOhcgeKsOBieH/fETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG4\n7QIDAQAB\n-----END PUBLIC KEY-----"

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
    