from fastapi import Body, FastAPI, status, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
import random
import time
from bson import Code
import json
import os
import uvicorn

# connection_str = "server-db:27017"
connection_str = "localhost:8223"
client = MongoClient(connection_str, connect=False)
db = client["server-db"]
print("Connected")

app = FastAPI()

# print(os.path.isfile("data/nrsr_2020/candidates_transformed.json"))

def getJsonFile(jsonFilePath):
    with open(jsonFilePath, encoding='utf8') as json_file:
        return json.load(json_file)

@app.get('/')
async def root ():
    return {'message': 'Server root'}

@app.post('/vote')
async def vote (
    token: str = Body(..., embed=True),
    vote: dict = Body(..., embed=True),
):
    data = {
        "token" : token,
        "candidate_id" : "1",
        "party_id" : "2",
        "office_id" : "2",
        "election_id" : "2"
    }

    db.votes.insert(data)

    return {
        'status' : 'success',
        'message': 'Vote processed',
        'vote' : vote,
        'token' : token
    }


def insertParty(party):
    res = db.parties.insert(party)
    return res

def insertCandidate(candidate, party_id_map):
    candidate["party_id"] = party_id_map[candidate["party_number"]]
    db.candidates.insert(candidate)  

# https://stackoverflow.com/questions/49616659/python-convert-recursively-to-string-in-list-of-dictionaries
def retype_object_id_to_str(data):
    to_map = retype_object_id_to_str
    if isinstance(data, list):
        return [to_map(x) for x in data]
    elif isinstance(data, dict):
        return {to_map(key): to_map(val) for key, val in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

@app.get('/elections/voting-data')
async def elections_voting_data():
    parties = list(db.parties.aggregate([
        {
            '$lookup': {
                'from': 'candidates', 
                'localField': '_id', 
                'foreignField': 'party_id', 
                'as': 'candidates'
            }
        }, {
            '$sort': {
                '_id': 1
            }
        }
    ]))

    parties = retype_object_id_to_str(parties)

    return {
        'status' : 'success',
        'message': 'Elections data',
        'data' : parties[0]
    }

@app.post('/import-data')
async def import_data():
    start_time = time.time()

    candidates = getJsonFile("data/nrsr_2020/candidates_transformed.json")
    parties = getJsonFile("data/nrsr_2020/parties_transformed.json")

    db.votes.remove({})
    db.candidates.remove({})
    db.parties.remove({})
    db.election_offices.remove({})
    
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

@app.get('/generate-keys')
async def test():
    keys = [
        {
            "public": "asdasd....",
            "private": "asd......."
        }
    ]
    return {
        'status' : 'success',
        'message': 'Keys generated successfully',
        'keys' : keys
    }

def validate_election_office(id, token):
    res = list(db.election_offices.find({id: id, token: token}))
    return len(res) > 0

def get_keys(collection):
    map = Code("function() { for (var key in this) { emit(key, null); } }")
    reduce = Code("function(key, stuff) { return null; }")
    result = db[collection].map_reduce(map, reduce, "myresults")
    return result.distinct('_id')

@app.get('/db/schema')
async def db_schema():
    info = {}

    collection_names = [collection for collection in client["server-db"].collection_names()]
    
    for name in collection_names:
        info[name] = get_keys(name)

    return {
        'status' : 'success',
        'message': 'DB schema',
        'info' : info
    }

@app.get('/statistics/progress')
async def statistics_progress():
    
    votes = list(db.votes.find({}))
    eligible_voters = 2 * (10**3)
    vote_participation = round(eligible_voters / len(votes), 5) if len(votes) else 0

    offices = db.election_offices.find({}).count()
    open_offices = 0
    closed_offices = offices - open_offices
    
    return {
        'status' : 'success',
        'message': 'Voting progress statistics',
        'statistics' : {
            "votes" : len(votes),
            "eligible_voters" : eligible_voters,
            "vote_participation" : vote_participation,
            "offices" : offices,
            "open_offices" : open_offices,
            "closed_offices" : closed_offices
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8222, reload=True)
