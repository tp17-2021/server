from fastapi import APIRouter

from pprint import pprint

from bson.objectid import ObjectId
from itertools import islice

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

from src.server.database import get_database
from src.server.routes.elastic import get_eligible_voters_per_locality
from src.server import config as c

# Create FastAPI router
router = APIRouter(
    prefix = "/statistics",
    tags = ["Statistics"],
)


@router.get('/live')
async def statistics_live():
    DB  = await get_database()

    votes = list(DB.votes.find({}))
    offices = DB.election_offices.find({}).count()
    open_offices = 0
    closed_offices = offices - open_offices

    return {
        'status': 'success',
        'message': 'Voting live statistics',
        'statistics': {
            "votes": len(votes),
            "offices": offices,
            "open_offices": open_offices,
            "closed_offices": closed_offices
        }
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

@router.get('/final')
async def statistics_final():
    DB  = await get_database()

    votes_n = await DB.votes.count_documents({})
    offices_n = await DB.election_offices.count_documents({})

    parties_votes_results = [result async for result in DB.votes.aggregate([
        {
            '$group': {
                '_id': '$party_id',
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                'count': -1
            }
        }, {
            '$lookup': {
                'from': 'parties',
                'localField': '_id',
                'foreignField': '_id',
                'as': 'party'
            }
        }, {
            '$unwind': {
                'path': '$party'
            }
        }
    ])]

    party_id_map = {}
    for party in parties_votes_results:
        party["candidates"] = []
        party_id_map[party["_id"]] = party


    candidates_votes_results = [result async for result in DB.votes.aggregate([
        {
            '$unwind': {
                'path': '$candidates'
            }
        }, {
            '$group': {
                '_id': '$candidates.candidate_id',
                'count': {
                    '$sum': 1
                }
            }
        }, {
            '$project': {
                'candidate_id': '$_id',
                'votes': '$count'
            }
        }, {
            '$lookup': {
                'from': 'candidates',
                'localField': 'candidate_id',
                'foreignField': '_id',
                'as': 'candidate'
            }
        }, {
            '$unwind': {
                'path': '$candidate'
            }
        }
    ])]

    for candidate_vote in candidates_votes_results:
        party_id = candidate_vote["candidate"]["party_id"]

        party_id_map[party_id]["candidates"].append(candidate_vote)

    result = []
    temporary_cut_result = []
    party_id_map = retype_object_id_to_str(party_id_map)
    for key, val in party_id_map.items():
        # print(val)
        # continue
        result.append(val)

    temporary_cut_result = result[0:1]
    pprint(temporary_cut_result) 
    temporary_cut_result[0]["candidates"] = temporary_cut_result[0]["candidates"][0:5]

    print("="*80)

    # TODO sort candidates by votes inside result 

    return {
        'status': 'success',
        'message': 'Voting final results',
        'statistics': {
            "votes": votes_n,
            "offices": offices_n,
            "parties_votes_results": retype_object_id_to_str(parties_votes_results[0]),
            "candidates_votes_results": retype_object_id_to_str(candidates_votes_results[0]),
            "overal_results": temporary_cut_result,
        }
    }
