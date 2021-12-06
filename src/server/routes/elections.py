from fastapi import APIRouter

import random
import os
from pprint import pprint
from bson.objectid import ObjectId
import json
import shutil

from src.server import schemas
from src.server.database import DB, CLIENT

# Create FastAPI router
router = APIRouter(
    prefix="/elections",
    tags=["Elections"],
)

def saveJson(data, filePath):
	if(".json" not in filePath):
		filePath += ".json"
	with open(f"{filePath}", "w", encoding='utf8') as write_file:
		json.dump(data, write_file, indent=4, ensure_ascii=False)

def validate_token(token):
    # todo
    return True

def validate_office(office_id):
    # todo
    return True

def validate_votes(request):
    # todo
    # office_key_pair = "xxxx"
    # try to decipher data with the private key somehow
    
    office_id = request.office_id
    votes = request.votes

    if not validate_office(office_id):
        return False

    for vote in votes:
        token = vote.token
        if not validate_token(token):
            return False

    return True


@router.post("/vote", response_model=schemas.ResponseServerVoteSchema)
async def vote (request: schemas.RequestServerVoteSchema):
    """
    Process candidate's vote
    """
    
    if not validate_votes(request):
        return {
            "status": "fail",
            "message": "Vote was not processed",
        }

    votes = request.votes
    # print(request)
    for vote in votes:
        vote = dict(vote)

        candidates = []
        for candidate in vote["candidates"]:
            candidate = dict(candidate)
            candidates.append(candidate)

        vote["candidates"] = candidates
        DB.votes.insert(vote)

    office_id = request.office_id
    return {
        "status": "success",
        "message": "Vote was processed",
        "votes": votes,
        "office_id": office_id
    }
    
@router.get("/seed/votes/{number}")
async def vote_seeder(number: int):
    """
    Immitate voting process
    """
    print(number)

    parties = get_parties_with_candidates()

    data_to_insert = []
    for _ in range(number):
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

# Configuration file for VT, development version
# curl -X "GET" "http://localhost:8222/elections/voting-data" -H "accept: application/json" > voting-data.json
@router.get('/voting-data')
async def elections_voting_data():
    
    # Parties and candidates data from DB
    parties = get_parties_with_candidates()
    parties = retype_object_id_to_str(parties)

    # Multilingual text for VT application
    texts = {
        "elections_name_short" : {
            "sk" : "Voľby do NRSR",
            "en" : "Parliamentary elections",
        },
        "elections_name_long" : {
            "sk" : "Voľby do národnej rady Slovenskej republiky",
            "en" : "Parliamentary elections of Slovak Republic",
        },
        "election_date" : {
            "sk" : "30.11.2021",
            "en" : "30.11.2021",
        }
    }

    # Combine all the data together
    data = {
        "parties" : parties,
        "texts" : texts
    }

    # Cntainer folder structure
    # data
    # src
    # ---- server
    # ---------- public
    # ---------------- config.zip
    # ---------------- nrsr_2020
    # -------------------------- logos
    # -------------------------- data.json


    public_dir_path = "src/server/public"
    data_path = os.path.join(public_dir_path, "nrsr_2020")
    if not os.path.exists(data_path):
        os.mkdir(data_path)

    logos_path = os.path.join(data_path, "logos")
    if not os.path.exists(logos_path):
        os.mkdir(logos_path)
        dest = shutil.copytree("data/nrsr_2020/logos/", "src/server/public/nrsr_2020/logos/", dirs_exist_ok=True)

    # file is accesible on /public/nrsr_2020/data.json
    saveJson(data, "src/server/public/nrsr_2020/data.json")    

    # make config file zip, downloadable at /public/config.zip
    shutil.make_archive("src/server/public/config", 'zip', "src/server/public/nrsr_2020/")

    return {
        'status' : 'success',
        'message': 'Elections data created',
        # 'data' : data
    }