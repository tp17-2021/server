import time
import json
import random
import os

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


@router.get("/schema", response_model=schemas.ResponseDatabaseSchema)
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

# TODO create schema for stored polling place
@router.post('/import-polling-places')
async def import_polling_places():
    start_time = time.time()
    
    DB.polling_places.drop()

    structures = getJsonFile("data/nrsr_2020/polling_places.json")
    data_to_insert = []

    for polling_place in structures:
        # TODO tu sa este doplnia dalsie info ako napriklad privatne kluce alebo to co bude treba
        data_to_insert.append(polling_place)

    DB.polling_places.insert_many(data_to_insert)
    polling_places_count = len(list(DB.polling_places.find({})))
    print(polling_places_count)

    return {
        'status' : 'success',
        'message': 'Polling places data imported',
        'polling_places_count' : polling_places_count,
        'time' : round(time.time() - start_time, 3)
    }

# TODO tuto treba overit podla schemy !!!!
@router.post('/import-data')
async def import_data():
    start_time = time.time()

    # we are in folder code in docker container and there is copy of src, data and requirements
    candidates = getJsonFile("data/nrsr_2020/candidates_transformed.json")
    parties = getJsonFile("data/nrsr_2020/parties_transformed.json")

    DB.votes.drop()
    DB.candidates.drop()
    DB.parties.drop()
    DB.election_offices.drop()
    
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