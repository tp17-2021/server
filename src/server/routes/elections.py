from fastapi import APIRouter

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
    DB.votes.insert(dict(request))

    return {
        "status": "success",
        "message": "Vote processed",
        "vote": dict(request)
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




@router.get('/voting-data')
async def elections_voting_data():
    parties = list(DB.parties.aggregate([
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