# General modules
from electiersa import electiersa

# FastAPI modules
from fastapi import APIRouter, status

# Server modules
from src.server import schemas
from src.server.database import get_database

# Create FastAPI router
router = APIRouter(
    prefix = "/encryption",
    tags = ["Encryption"],
)


@router.post("/key-pairs", response_model=schemas.Message)
async def create_key_pairs_for_polling_places() -> dict:
    """ Create key pairs for polling places """

    DB  = await get_database()
    
    # TODO toto potom odkomentovat
    # DB.key_pairs.drop()

    # TODO toto potom odstranit
    count = 0
    N = 0
    # ---

    polling_place_ids = [doc["_id"] async for doc in DB.polling_places.find({}, {"_id": 1})]
    polling_place_ids_key_pairs = [doc["polling_place_id"] async for doc in DB.key_pairs.find({}, {"polling_place_id": 1, "_id": 0})]

    for polling_place_id in polling_place_ids:
        if polling_place_id not in polling_place_ids_key_pairs:
            private_key_pem, public_key_pem = electiersa.get_rsa_key_pair()
            g_private_key_pem, g_public_key_pem = electiersa.get_rsa_key_pair()

            key_pair = {
                "_id": polling_place_id,
                "polling_place_id": polling_place_id,
                "private_key_pem": private_key_pem,
                "public_key_pem": public_key_pem,
                "g_private_key_pem": g_private_key_pem,
                "g_public_key_pem": g_public_key_pem
            }
            await DB.key_pairs.insert_one(key_pair)

        # TODO toto potom odstranit
        count += 1
        if count > N:
            break
        # ---

    content = {
        "status": "success",
        "message": "RSA cryptography keys successfully generated"
    }
    return content
