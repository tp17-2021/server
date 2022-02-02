import os
import motor.motor_asyncio

CLIENT = motor.motor_asyncio.AsyncIOMotorClient(
    f"{os.environ['SERVER_DB_HOST']}:{os.environ['SERVER_DB_PORT']}"
)
DB = CLIENT[os.environ["SERVER_DB_NAME"]]


async def get_parties_with_candidates():
    pipeline = [{
        "$lookup": {
            "from": "candidates",
            "localField": "party_number",
            "foreignField": "party_number",
            "as": "candidates"
        }
    }]
    parties_with_candidates = [party_with_candidate async for party_with_candidate in DB.parties.aggregate(pipeline)]
    return parties_with_candidates

async def get_max_id(collection_name):
    ids = [item["_id"] async for item in DB[collection_name].find()]
    ids.sort()
    max_id = ids[-1]
    return max_id