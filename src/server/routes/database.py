import time
import json
import random

from bson import Code

from fastapi import APIRouter

from src.server import schemas
from src.server.database import DB, CLIENT

# Create FastAPI router
router = APIRouter(
    prefix="/database",
    tags=["Database"],
)


def get_keys(collection_name: str):
    """
    Get all keys from provided collection
    """
    map = Code("function() { for (var key in this) { emit(key, null); } }")
    reduce = Code("function(key, stuff) { return null; }")
    result = DB[collection_name].map_reduce(map, reduce, "myresults")
    return result.distinct('_id')


@router.get("/schema", tags=["Database"], response_model=schemas.ResponseDBSchema)
async def db_schema():
    """
    Get all collections from database
    """
    collections = []

    collection_names = [collection_name for collection_name in CLIENT["server-db"].collection_names()]    
    for collection_name in collection_names:
        collection_keys = get_keys(collection_name)
        collections.append({
            "name": collection_name,
            "keys": collection_keys
        })

    return {
        "status": "success",
        "message": "DB schema",
        "collections": collections
    }

def getJsonFile(jsonFilePath):
    with open(jsonFilePath, encoding='utf8') as json_file:
        return json.load(json_file)


def insertParty(party):
    res = DB.parties.insert(party)
    return res


def insertCandidate(candidate, party_id_map):
    candidate["party_id"] = party_id_map[candidate["party_number"]]
    DB.candidates.insert(candidate)  


@router.post('/import-data')
async def import_data():
    start_time = time.time()

    candidates = getJsonFile("data/nrsr_2020/candidates_transformed.json")
    parties = getJsonFile("data/nrsr_2020/parties_transformed.json")

    DB.votes.remove({})
    DB.candidates.remove({})
    DB.parties.remove({})
    DB.election_offices.remove({})
    
    sample_candidate = {
        "id": random.randint(10**6, 10**7),
        "order" : random.randint(10, 10000),
        "first_name" : "Jozef",
        "last_name" : "Králik",
        "middle_names" : "Jožko",
        "degrees_before" : "Ing. Mgr.",
        "degrees_after" : "PhD.",
        "personal_number" : "EL180968",
        "occupation": "Calisthenics enthusiast, crypto trader, physicist, daš si hrozienko?",
        "age" : random.randint(18, 110),
        "residence": "Prievidza",
        "party_id" : "1"
    }

    sample_party = {
        "id": 19,
        "name": "SMER - sociálna demokracia",
        "abbreviation": "SMER - SD",
        "image": "don_roberto_logo.jpg"
    }

    party_id_map = {}

    for party in parties:
        id = insertParty(party)
        party_id_map[party["party_number"]] = id

    # print(party_id_map)

    for candidate in candidates:
        insertCandidate(candidate, party_id_map)

    return {
        'status' : 'success',
        'message': 'Voting data imported',
        'time' : round(time.time() - start_time, 3)
    }