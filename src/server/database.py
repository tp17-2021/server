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


async def get_test_parties_with_candidates():
    pipeline = [{
        "$lookup": {
            "from": "test_candidates",
            "localField": "party_number",
            "foreignField": "party_number",
            "as": "candidates"
        }
    }]
    parties_with_candidates = [party_with_candidate async for party_with_candidate in DB.test_parties.aggregate(pipeline)]
    return parties_with_candidates