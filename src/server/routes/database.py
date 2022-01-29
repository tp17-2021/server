# General modules
import json
from bson import Code
import traceback
import base64


# Cryptography libraries
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# FastAPI modules
from fastapi import APIRouter, status
from starlette.responses import JSONResponse


# Server modules
from src.server import config
from src.server import schemas
from src.server.database import DB
from src.server.schemas import PollingPlace, RequestEncryptionDecryptionTestSchema

# we are in folder 'code' in docker container and there is a copy of src, data and requirements
CANDIDATES_JSON = "data/nrsr_2020/candidates_transformed.json"
PARTIES_JSON = "data/nrsr_2020/parties_transformed.json"
POLLING_PLACES_JSON = "data/nrsr_2020/polling_places.json"

# Create FastAPI router
router = APIRouter(
    prefix = "/database",
    tags = ["Database"],
)


async def load_json(path):
    """
    Helper to load json file
    """
    with open(path, encoding="utf8") as file:
        return json.load(file)


@router.post("/import-data", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={500: {"model": schemas.Message}})
async def import_data():
    global CANDIDATES_JSON, PARTIES_JSON

    try:
        DB.parties.drop()
        DB.candidates.drop()
        DB.polling_places.drop()

        parties = await load_json(PARTIES_JSON)
        for party in parties:
            await DB.parties.insert_one(party)

        candidates = await load_json(CANDIDATES_JSON)
        for candidate in candidates:
            await DB.candidates.insert_one(candidate)

        polling_places = await load_json(POLLING_PLACES_JSON)
        for polling_place in polling_places:
            await DB.polling_places.insert_one(polling_place)

        content = {
            "status": "success",
            "message": "Voting data was successfully imported"
        }
        return content

    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


# https://stackoverflow.com/a/48117846
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
                print(collection_name, collection_keys)
                collections.append({
                    "name": collection_name,
                    "keys": collection_keys
                })

        return {
            "collections": collections
        }
    
    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)

