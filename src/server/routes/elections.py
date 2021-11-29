from fastapi import APIRouter

import random
from pprint import pprint
from bson.objectid import ObjectId

from src.server import schemas
from src.server.database import DB, CLIENT

# Create FastAPI router
router = APIRouter(
    prefix="/elections",
    tags=["Elections"],
)


@router.post("/vote", response_model=schemas.ResponseVoteSchema)
async def vote (request: schemas.RequestVoteSchema):
    """
    Process candidate's vote
    """
    
    office_id = request["office_id"]

    # validate token and room
    if(True or "office id exists"):
        office_key_pair = "xxxx"

        # try to decipher data with the private key somehow
        
    print(f"{office_id=}")
    
    # DB.votes.insert(dict(request))

    return {
        "status": "success",
        "message": "Vote processed",
        "vote": dict(request)
    }

@router.get("/seed/votes/{number}")
async def vote_seeder(number: int):
    """
    Immitate voting process
    """
    print(number)

    parties = get_parties_with_candidates()

    data_to_insert = []
    for x in range(number):
        selected_party = random.choice(parties)
        vote = {
            "token": "token",
            "party_id" : selected_party["_id"],
            "election_id" : "hqgwdhjgjasd",
            "office_id" : "khkjehwdkjhaskd",
            "candidates" : []
        }

        selected_candidates = random.sample(selected_party["candidates"], 5)

        for candidate in selected_candidates:
            vote["candidates"].append({
                "candidate_id" : candidate["_id"]
            })
       
        data_to_insert.append(vote)

    DB.votes.insert_many(data_to_insert)

    return {
        "status": "success",
        "message": "Vote processed",
        "votes": []
    }

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

# Get list of parties with nested objects of candidates
def get_parties_with_candidates():
    return list(DB.parties.aggregate([
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

@router.get('/voting-data')
async def elections_voting_data():
    
    parties = get_parties_with_candidates()
    parties = retype_object_id_to_str(parties)

    return {
        'status' : 'success',
        'message': 'Elections data',
        'data' : parties[0]
    }