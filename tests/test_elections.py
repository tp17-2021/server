import nest_asyncio
nest_asyncio.apply()
__import__('IPython').embed()

import pytest
import asyncio

import os
import motor.motor_asyncio

from unittest import mock 
from tests import envs

from electiersa import electiersa

with mock.patch.dict(os.environ, envs.envs):
    from src.server.app import app

from fastapi.testclient import TestClient

from src.server.database import connect_to_mongo

client = TestClient(app)

VERBOSE = True

def connect_to_db() -> motor.motor_asyncio.AsyncIOMotorClient:
    """ Connec to database """

    clinet = motor.motor_asyncio.AsyncIOMotorClient(
        f"{os.environ['SERVER_DB_HOST']}:{os.environ['SERVER_DB_PORT']}"
    )
    db = clinet[os.environ["SERVER_DB_NAME"]]
    _ = str(db)
    return db


def set_vote(
    token: str = "fjosjfidsw",
    party_id: int = 10,
    election_id: str = "election_id",
    candidate_ids: list = [1075, 1076, 1077]) -> dict:
    
    """ Initialize default vote """

    vote = {
        "token": token,
        "party_id": party_id,
        "election_id": election_id,
        "candidate_ids": candidate_ids
    }
    return vote


async def get_pems(
    db: motor.motor_asyncio.AsyncIOMotorClient,
    polling_place_id: int,
    g_private_key_pem: str = "valid",
    public_key_pem: str = "valid") -> tuple:

    """ Return pems """

    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    if g_private_key_pem == "valid":
        g_private_key_pem = key_pair["g_private_key_pem"]

    if public_key_pem == "valid":
        public_key_pem = key_pair["public_key_pem"]

    return g_private_key_pem, public_key_pem


def set_headers(
    accept: str = "application/json",
    content_type: str = "application/json") -> dict:

    """ Initialize default headers """

    headers = {
        "accept": accept,
        "Content-Type": content_type,
    }
    return headers


@pytest.mark.asyncio
async def test_valid_data():
    """
    Test when everything is valid such as polling_place_id, g_private_key_pem,
    public_key_pem, token, party_id, election_id, candidate_ids
    """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote()
    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_invalid_g_private_key_pem():
    """ Test invalid gateway's private key pem """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
    
    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db,
                                                       polling_place_id,
                                                       g_private_key_pem="invalid_g_private_key_pem")

    vote = set_vote()

    try:
        electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)
    except:
        assert True


@pytest.mark.asyncio
async def test_invalid_public_key_pem():
    """ Test invalid public key pem """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
    
    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db,
                                                       polling_place_id,
                                                       public_key_pem="invalid_public_key_pem")

    vote = set_vote()

    try:
        electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)
    except:
        assert True


@pytest.mark.asyncio
async def test_invalid_pems():
    """ Test invalid gateway's private key pem and public key pem """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
    
    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db,
                                                       polling_place_id,
                                                       g_private_key_pem = "invalid_private_key_pem",
                                                       public_key_pem="invalid_public_key_pem")

    vote = set_vote()

    try:
        electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)
    except:
        assert True


@pytest.mark.asyncio
async def test_duplicated_token():
    """ Test duplicated token in the payload """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
    
    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote()

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__,
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_invalid_party_id():
    """ Test no occurrence in database for selected party id """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote(party_id=-1)

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_no_party_id():
    """ Test vote without party id is still valid vote """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote(party_id=None, candidate_ids=[])

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_invalid_election_id():
    """ Test no occurrence in database for selected election id """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
    
    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote(election_id="no_match_election_id")

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_invalid_candidate_ids_1():
    """ Test more than 5 candidate ids """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
 
    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote(candidate_ids=[1075, 1076, 1077, 1078, 1079, 1080])

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_invalid_candidate_ids_2():
    """ Test duplicate candidate ids """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
    
    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote(candidate_ids=[1075, 1075])

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_invalid_candidate_ids_3():
    """ Test no occurrence in database for selected candidate id """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote(candidate_ids=[-1])

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_invalid_candidate_ids_4():
    """ Test invalid candidate id for selected polling place id """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
    
    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote(candidate_ids=[0])

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_no_candidates():
    """ Test vote without candidates is still valid vote """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
    
    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote(candidate_ids=[])

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_duplicated_vote():
    """ Test insert same vote twice """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
    
    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote()

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    client.post("/elections/vote", headers=headers, json=payload)
    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_invalid_combination_of_party_id_and_candidate_ids():
    """
    Test if there is no possibility to have party id set to None and non empty
    list of candidate ids
    """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    db.votes.drop()

    polling_place_id = 0
    g_private_key_pem, public_key_pem = await get_pems(db, polling_place_id)

    vote = set_vote(party_id=None, candidate_ids=[1075])

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = set_headers()

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote.__dict__
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    if VERBOSE:
        print(response.text)

    assert response.status_code == 400