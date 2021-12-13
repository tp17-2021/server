# General modules
import time
import json
import random
import os
from Crypto import PublicKey
from bson import Code

# Cryptography libraries
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import binascii

# FastAPI modules
from fastapi import APIRouter, status, HTTPException, Body
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

# Server modules
from src.server import schemas
from src.server.database import DB, CLIENT
from src.server.schemas import ServerPollingPlace, RequestEncryptionDecryptionTestSchema

# Create FastAPI router
router = APIRouter(
    prefix="/database",
    tags=["Database"],
)

def get_keys(collection_name: str):
    """
    Get all keys from provided collection. Helper funkcion that emits all key inside collection using mapreduce.
    """
    map = Code("function() { for (var key in this) { emit(key, null); } }")
    reduce = Code("function(key, stuff) { return null; }")
    result = DB[collection_name].map_reduce(map, reduce, "myresults")
    return result.distinct('_id')


@router.get("/schema", response_model=schemas.ResponseDatabaseSchema)
async def db_schema():
    """
    Get all collections from database
    """
    collections = []

    collection_names = [
        collection_name for collection_name in CLIENT["server-db"].collection_names()]
    for collection_name in collection_names:
        collection_keys = get_keys(collection_name)
        collections.append({
            "name": collection_name,
            "keys": collection_keys
        })

    return {
        "status": "success",
        "message": "DB schema",
        "collections": collections
    }

# helper to open json file
def getJsonFile(jsonFilePath):
    jsonFilePath = f'{jsonFilePath}.json' if ".json" not in jsonFilePath else jsonFilePath
    with open(jsonFilePath, encoding='utf8') as json_file:
        return json.load(json_file)

# repository function for inserting one party
def insertParty(party):
    res = DB.parties.insert_one(party)
    return res

# repository function for inserting one party
def insertCandidate(candidate, party_id_map):
    candidate["party_id"] = party_id_map[candidate["party_number"]]
    res = DB.candidates.insert_one(candidate)
    return res

# TODO create schema for stored polling place
@router.post('/import-polling-places')
async def import_polling_places():
    start_time = time.time()

    DB.polling_places.drop()

    structures = getJsonFile("data/nrsr_2020/polling_places.json")
    data_to_insert = []

    for polling_place in structures:

        try:
            polling_place_model = ServerPollingPlace(**polling_place)
        except Exception as e:
            print(f"Error parsong ServerPollingPlace: {e}")
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error parsong ServerPollingPlace: {e}"
            )

        # TODO tu sa este doplnia dalsie info ako napriklad privatne kluce alebo to co bude treba
        data_to_insert.append(polling_place)

    DB.polling_places.insert_many(data_to_insert)
    polling_places_count = len(list(DB.polling_places.find({})))
    print(polling_places_count)

    return {
        'status': 'success',
        'message': 'Polling places data imported',
        'polling_places_count': polling_places_count,
        'time': round(time.time() - start_time, 3)
    }


def encryptMsg(data, pubKey):
	msg = str.encode(data)
	encryptor = PKCS1_OAEP.new(pubKey)
	encrypted = encryptor.encrypt(msg)
	# print("Encrypted:", binascii.hexlify(encrypted))
	return encrypted
	

def decryptMsg(data, keyPair):
	decryptor = PKCS1_OAEP.new(keyPair)
	decrypted = decryptor.decrypt(data)
	return decrypted
	# print('Decrypted:', decrypted)

# OAEP padding algorithm
def getRSAKeyPair():
	KEY_LENGTH = 4096

	keyPair = RSA.generate(KEY_LENGTH)
	pubKey = keyPair.publickey()
	# print(f"Public key:  (n={hex(pubKey.n)}, e={hex(pubKey.e)})")

	pubKeyPEM = pubKey.exportKey()
	# print(pubKeyPEM.decode('ascii'))

	# print(f"Private key: (n={hex(pubKey.n)}, d={hex(keyPair.d)})")
	privKeyPEM = keyPair.exportKey()

	# print(privKeyPEM.decode('ascii'))

	return keyPair, pubKey, pubKeyPEM, privKeyPEM

@router.post('/create-key-pairs')
async def create_key_paris_for_polling_places():
    start_time = time.time()

    keyPair, pubKey, pubKeyPEM, privKeyPEM = getRSAKeyPair()

    DB.key_pairs.insert_one({
        "polling_place_id" : "123456",
        "private_key_pem" : privKeyPEM.decode('ascii'),
        "public_key_pem" : pubKeyPEM.decode('ascii')
    })

    return {
        'status': 'success',
        'message': 'RSA cryptography keys generated',
        'time': round(time.time() - start_time, 3)
    }

@router.post('/test-encryption-decryption')
async def test_encryption_decryption(request: RequestEncryptionDecryptionTestSchema):

    print(request)
    print("asd")
    return request
    # initial_data = "Hi, this is my secret vote"
    initial_data = request
    initial_data = json.dumps(initial_data)

    # get first random key pair from DB
    random_key_pair = list(DB.key_pairs.find({}))

    if not len(random_key_pair):
        print("err")
        # raise exception here
    random_key_pair = random_key_pair[0]

    # get values from DB object
    public_key_pem, private_key_pem = random_key_pair["public_key_pem"], random_key_pair["private_key_pem"]

    # Import HEX keys, get key objects
    public_key = RSA.import_key(public_key_pem)
    private_key = RSA.import_key(private_key_pem)

    encrypted_data = encryptMsg(initial_data, public_key)
    decrypted_data = decryptMsg(encrypted_data, private_key).decode('ascii')

    print(encrypted_data)
    print(decrypted_data)

    return {
        'status': 'success',
        'data' : {
            'initial_data': json.loads(initial_data),
            'encrypted_data': str(encrypted_data),
            'decrypted_data': json.loads(str(decrypted_data))
        },
        'message': 'RSA cryptography keys generated',
    }

# TODO tuto treba overit podla schemy !!!!
@router.post('/import-data')
async def import_data():
    start_time = time.time()

    # we are in folder code in docker container and there is copy of src, data and requirements
    candidates = getJsonFile("data/nrsr_2020/candidates_transformed.json")
    parties = getJsonFile("data/nrsr_2020/parties_transformed.json")

    DB.votes.drop()
    DB.candidates.drop()
    DB.parties.drop()
    DB.election_offices.drop()

    sample_candidate = {
        "id": random.randint(10**6, 10**7),
        "order": random.randint(10, 10000),
        "first_name": "Jozef",
        "last_name": "Králik",
        "middle_names": "Jožko",
        "degrees_before": "Ing. Mgr.",
        "degrees_after": "PhD.",
        "personal_number": "EL180968",
        "occupation": "Calisthenics enthusiast, crypto trader, physicist, daš si hrozienko?",
        "age": random.randint(18, 110),
        "residence": "Prievidza",
        "party_id": "1"
    }

    sample_party = {
        "id": 19,
        "name": "SMER - sociálna demokracia",
        "abbreviation": "SMER - SD",
        "image": "don_roberto_logo.jpg"
    }

    party_id_map = {}

    for party in parties:
        id = insertParty(party)
        id = id.inserted_id
        print(id)
        party_id_map[party["party_number"]] = id

    # print(party_id_map)

    for candidate in candidates:
        res = insertCandidate(candidate, party_id_map)

    return {
        'status': 'success',
        'message': 'Voting data imported',
        'time': round(time.time() - start_time, 3)
    }
