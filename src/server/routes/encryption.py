# General modules
import traceback
from electiersa import electiersa

# FastAPI modules
from fastapi import APIRouter, status
from starlette.responses import JSONResponse

# Server modules
from src.server import config
from src.server import schemas
from src.server.database import get_database

# Create FastAPI router
router = APIRouter(
    prefix = "/encryption",
    tags = ["Encryption"],
)


@router.post("/key-pairs", response_model=schemas.Message, status_code=status.HTTP_200_OK)
async def create_key_pairs_for_polling_places():
    DB  = await get_database()
    
    # DB.key_pairs.drop()

    # --- toto potom odstranit
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


@router.post("/test-encrypt-vote", response_model=schemas.VoteEncrypted, status_code=status.HTTP_200_OK)
async def test_encrypt_vote(request: schemas.VoteToBeEncrypted):
    vote = request.vote
    vote = dict(vote)
    g_private_key_pem = request.g_private_key_pem
    public_key_pem = request.public_key_pem
        
    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)
    return encrypted_vote


@router.post("/test-decrypt-vote", response_model=schemas.Vote, status_code=status.HTTP_200_OK)
async def test_decrypt_vote(request: schemas.VoteToBeDecrypted):
    encrypted_vote = request.encrypted_vote
    private_key_pem = request.private_key_pem
    g_public_key_pem = request.g_public_key_pem

    vote = electiersa.decrypt_vote(encrypted_vote, private_key_pem, g_public_key_pem)
    return vote


@router.post("/test-encrypt-commission-paper")
async def test_encrypt_vote(request: schemas.CommissionPaperToBeEncrypted):
    vote = request.vote
    vote = dict(vote)
    g_private_key_pem = request.g_private_key_pem
    public_key_pem = request.public_key_pem
        
    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)
    return encrypted_vote


@router.post("/test-decrypt-commission-paper")
async def test_decrypt_vote(request: schemas.CommissionPaperToBeDecrypted):
    encrypted_vote = request.encrypted_vote
    private_key_pem = request.private_key_pem
    g_public_key_pem = request.g_public_key_pem

    vote = electiersa.decrypt_vote(encrypted_vote, private_key_pem, g_public_key_pem)
    return vote