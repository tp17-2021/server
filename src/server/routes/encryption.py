# General modules
import traceback
from rsaelectie import rsaelectie

# FastAPI modules
from fastapi import APIRouter, status
from starlette.responses import JSONResponse

# Server modules
from src.server import config
from src.server import schemas
from src.server.database import DB

# Create FastAPI router
router = APIRouter(
    prefix = "/encryption",
    tags = ["Encryption"],
)


@router.post("/key-pairs", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={500: {"model": schemas.Message}})
async def create_key_pairs_for_polling_places():
    try:
        # DB.key_pairs.drop()

        # --- toto potom odstranit
        count = 0
        N = 0
        # ---

        polling_place_ids = [doc["_id"] async for doc in DB.polling_places.find({}, {"_id": 1})]
        polling_place_ids_key_pairs = [doc["polling_place_id"] async for doc in DB.key_pairs.find({}, {"polling_place_id": 1, "_id": 0})]

        for polling_place_id in polling_place_ids:
            if polling_place_id not in polling_place_ids_key_pairs:
                private_key_pem, public_key_pem = await rsaelectie.get_rsa_key_pair()

                private_key_pem = private_key_pem.decode("utf-8")
                public_key_pem = public_key_pem.decode("utf-8")

                key_pair = {
                    "polling_place_id": polling_place_id,
                    "private_key_pem": private_key_pem,
                    "public_key_pem": public_key_pem
                }
                await DB.key_pairs.insert_one(key_pair)

            # --- toto potom odstranit
            count += 1
            if count > N:
                break
            # ---

        content = {
            "status": "success",
            "message": "RSA cryptography keys successfully generated"
        }
        return content

    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


@router.post("/test-encrypt-vote", response_model=schemas.VoteEncrypted, status_code=status.HTTP_200_OK, responses={500: {"model": schemas.Message}})
async def test_encrypt_vote(request: schemas.VoteToBeEncrypted):
    try:
        public_key_pem = request.public_key_pem

        data_to_be_encrypted = request.vote
        data_to_be_encrypted = dict(data_to_be_encrypted)

        encrypted_vote = await rsaelectie.encrypt_vote(public_key_pem, data_to_be_encrypted)

        content = {
            "encrypted_vote": encrypted_vote
        }
        return content
        
    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


@router.post("/test-decrypt-vote", response_model=schemas.Vote, status_code=status.HTTP_200_OK, responses={500: {"model": schemas.Message}})
async def test_decrypt_vote(request: schemas.VoteToBeDecrypted):
    try:
        private_key_pem = request.private_key_pem
        vote_to_be_decrypted = request.encrypted_vote

        vote = await rsaelectie.decrypt_vote(private_key_pem, vote_to_be_decrypted)
        return vote

    except:
        traceback.print_exc()
        content = {
            "status": "failure",
            "message": "Internal server error"
        }
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)
