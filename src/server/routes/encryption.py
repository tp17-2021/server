# General modules
import json
from bson import Code
import traceback
import base64


# # Cryptography libraries
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

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


async def encrypt_message(message, public_key):
    encryptor = PKCS1_OAEP.new(public_key)
    encrypted = encryptor.encrypt(bytes(message, encoding="utf-8"))
    return base64.b64encode(encrypted)


async def decrypt_message(base64_encoded_message, private_key):
    decrypted = base64.b64decode(base64_encoded_message)
    decryptor = PKCS1_OAEP.new(private_key)
    return decryptor.decrypt(decrypted)


@router.post("/key-pairs", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={500: {"model": schemas.Message}})
async def create_key_pairs_for_polling_places():
    try:
        DB.key_pairs.drop()

        count = 0
        polling_places = [polling_place async for polling_place in DB.polling_places.find()]
        for polling_place in polling_places:
            polling_place_id = str(polling_place["_id"])

            private_key_pem, public_key_pem = await rsaelectie.get_rsa_key_pair(config.KEY_LENGTH)

            private_key_pem = private_key_pem.decode("utf-8")
            public_key_pem = public_key_pem.decode("utf-8")
            
            key_pair = {
                "polling_place_id": polling_place_id,
                "private_key_pem": private_key_pem,
                "public_key_pem": public_key_pem
            }
            await DB.key_pairs.insert_one(key_pair)
            
            # --------
            # todo - toto potom odstranit
            count += 1
            if count > 0:
                break
            # --------

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


# @router.post("/encrypt-vote", response_model=schemas.VoteEncrypted, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
# async def encrypt_data(request: schemas.VoteToBeEncrypted):
#     try:
#         public_key_pem = request.public_key_pem

#         polling_place_id = request.polling_place_id

#         data_to_be_encrypted = request.data
#         data_to_be_encrypted = dict(data_to_be_encrypted)
#         data_to_be_encrypted = json.dumps(data_to_be_encrypted)

#         try:
#             public_key_pem = public_key_pem.encode("utf-8")
#             public_key = RSA.import_key(public_key_pem)

#             encrypted_data = await encrypt_message(data_to_be_encrypted, public_key)
#             encrypted_data = encrypted_data.decode("utf-8")

#             content = {
#                 "polling_place_id": polling_place_id,
#                 "data": encrypted_data
#             }
#             return content

#         except:
#             traceback.print_exc()
#             content = {
#                 "status": "failure",
#                 "message": "RSA key format is not supported"
#             }
#             return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)

#     except:
#         traceback.print_exc()
#         content = {
#             "status": "failure",
#             "message": "Internal server error"
#         }
#         return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)


# @router.post("/decrypt-vote", response_model=schemas.VoteDecrypted, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
# async def decrypt_vote(request: schemas.VoteEncrypted):
#     try:
#         polling_place_id = request.polling_place_id
        
#         data_to_be_decrypted = request.data

#         key_pairs = [key_pair async for key_pair in DB.key_pairs.find()]
#         for key_pair in key_pairs:
#             if key_pair["polling_place_id"] == polling_place_id:

#                 try:
#                     private_key_pem = key_pair["private_key_pem"]
#                     private_key_pem = private_key_pem.encode("utf-8")

#                     private_key = RSA.import_key(private_key_pem)

#                     decrypted_data = await decrypt_message(data_to_be_decrypted, private_key)
#                     decrypted_data = decrypted_data.decode("utf-8")
#                     decrypted_data = json.loads(decrypted_data)

#                     content = {
#                         "polling_place_id": polling_place_id,
#                         "data": decrypted_data
#                     }
#                     return content

#                 except:
#                     traceback.print_exc()
#                     content = {
#                         "status": "failure",
#                         "message": "Incorrect decryption"
#                     }
#                     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)

#     except:
#         traceback.print_exc()
#         content = {
#             "status": "failure",
#             "message": "Internal server error"
#         }
#         return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content)
