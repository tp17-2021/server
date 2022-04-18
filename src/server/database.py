import os
import motor.motor_asyncio


DB: motor.motor_asyncio.AsyncIOMotorClient = None


async def connect_to_mongo() -> None:
    """ Connect to mongo database """
    global DB
    
    CLIENT = motor.motor_asyncio.AsyncIOMotorClient(
        f"{os.environ['SERVER_DB_HOST']}:{os.environ['SERVER_DB_PORT']}"
    )
    DB = CLIENT[os.environ["SERVER_DB_NAME"]]    


async def get_database() -> motor.motor_asyncio.AsyncIOMotorClient:
    """ Get database instance """
    if DB is None:
        await connect_to_mongo()
    return DB


async def get_parties_with_candidates():
    """ Return aggregated parties with candidates """
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

# TODO prerobit, toto neni dobre (treba na urovni db spravit)
async def get_max_id(collection_name: str) -> int:
    """ Return maximum id from provided collection name """
    # ids = [doc["_id"] async for doc in DB[collection_name].find({}, {"_id":1})]
    # ids.sort()
    # if len(ids) == 0:
    #     max_id = -1
    # else:
    #     max_id = ids[-1]
    # return max_id

    id  = DB[collection_name].find({}, {"_id":1}).sort({"_id":-1}).limit(1)
    return id