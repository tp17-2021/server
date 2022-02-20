import nest_asyncio
nest_asyncio.apply()
__import__('IPython').embed()

import os
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

def connect_to_db():
    clinet = motor.motor_asyncio.AsyncIOMotorClient(
        f"{os.environ['SERVER_DB_HOST']}:{os.environ['SERVER_DB_PORT']}"
    )
    db = clinet[os.environ["SERVER_DB_NAME"]]
    _ = str(db)
    print(_)
    return db


@pytest.mark.asyncio
async def test_vote_valid_data():
    """
    Everything is valid: aes_key, public_key_pem, polling_place_id, token, party_id, election_id, candidates_ids
    """

    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = key_pair["g_private_key_pem"]
    public_key_pem = key_pair["public_key_pem"]

    vote = {
        "token": "fjosjfidsw",
        "party_id": 10,
        "election_id": "election_id",
        "candidates_ids": [
            1075,
            1076,
            1077
        ]
    }

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_vote_duplicate_tokens():
    """
    Duplicate tokens in the batch
    """
    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = key_pair["g_private_key_pem"]
    public_key_pem = key_pair["public_key_pem"]

    vote = {
        "token": "eggc0tddwl",
        "party_id": 10,
        "election_id": "election_id",
        "candidates_ids": [
            1075,
            1076,
            1077
        ]
    }

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote,
            encrypted_vote
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_vote_invalid_combination_of_token_and_polling_place_id():
    """
    Invalid token and polling place id: combination already in database
    """
    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = key_pair["g_private_key_pem"]
    public_key_pem = key_pair["public_key_pem"]

    vote = {
        "token": "eggc0tddwl",
        "party_id": 10,
        "election_id": "election_id",
        "candidates_ids": [
            1075,
            1076,
            1077
        ]
    }

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote
        ]
    }

    client.post("/elections/vote", headers=headers, json=payload)
    response = client.post("/elections/vote", headers=headers, json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_vote_invalid_party_id():
    """
    Invalid party id: no occurrence in database
    """
    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = key_pair["g_private_key_pem"]
    public_key_pem = key_pair["public_key_pem"]

    vote = {
        "token": "fjosjfidsw",
        "party_id": -1,
        "election_id": "election_id",
        "candidates_ids": [
            1075,
            1076,
            1077
        ]
    }

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_vote_invalid_election_id():
    """
    Invalid election id: no match
    """
    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
  
    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = key_pair["g_private_key_pem"]
    public_key_pem = key_pair["public_key_pem"]

    vote = {
        "token": "fjosjfidsw",
        "party_id": 10,
        "election_id": "no_match_election_id",
        "candidates_ids": [
            1075,
            1076,
            1077
        ]
    }

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_vote_more_than_5_candidates():
    """
    Invalid candidates: more than 5
    """
    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = key_pair["g_private_key_pem"]
    public_key_pem = key_pair["public_key_pem"]

    vote = {
        "token": "fjosjfidsw",
        "party_id": 10,
        "election_id": "election_id",
        "candidates_ids": [
            1075,
            1076,
            1077,
            1078,
            1079,
            1080
        ]
    }

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_vote_duplicate_candidates():
    """
    Invalid candidates: duplicate ids
    """
    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = key_pair["g_private_key_pem"]
    public_key_pem = key_pair["public_key_pem"]

    vote = {
        "token": "fjosjfidsw",
        "party_id": 10,
        "election_id": "election_id",
        "candidates_ids": [
            1075,
            1075
        ]
    }

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_vote_invalid_candidate_id0():
    """
    Invalid candidate id: no occurrence in database
    """
    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = key_pair["g_private_key_pem"]
    public_key_pem = key_pair["public_key_pem"]

    vote = {
        "token": "fjosjfidsw",
        "party_id": 10,
        "election_id": "election_id",
        "candidates_ids": [
            -1
        ]
    }

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_vote_invalid_candidate_id1():
    """
    Invalid candidate id: wrong id for entered party id
    """
    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = key_pair["g_private_key_pem"]
    public_key_pem = key_pair["public_key_pem"]

    vote = {
        "token": "fjosjfidsw",
        "party_id": 10,
        "election_id": "election_id",
        "candidates_ids": [
            0
        ]
    }

    encrypted_vote = electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote
        ]
    }

    response = client.post("/elections/vote", headers=headers, json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_vote_invalid_g_private_key_pem():
    """
    Invalid gateway private key pem
    """
    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = "invalid_g_private_key_pem"
    public_key_pem = key_pair["public_key_pem"]

    vote = {
        "token": "fjosjfidsw",
        "party_id": 10,
        "election_id": "election_id",
        "candidates_ids": [
            0
        ]
    }

    try:
        electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)
    except:
        assert True


@pytest.mark.asyncio
async def test_vote_invalid_public_key_pem():
    """
    Invalid public key pem
    """
    db = connect_to_db()
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    polling_place_id = 0
    key_pair = await db.key_pairs.find_one({"polling_place_id": polling_place_id}, {"_id":0})
    g_private_key_pem = key_pair["g_private_key_pem"]
    public_key_pem = "invalid_public_key_pem"

    vote = {
        "token": "fjosjfidsw",
        "party_id": 10,
        "election_id": "election_id",
        "candidates_ids": [
            0
        ]
    }

    try:
        electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)
    except:
        assert True


@pytest.mark.asyncio
async def test_vote_invalid_keys():
    """
    Invalid keys: Wrong gatewas private key pem and public key pem
    """
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    g_private_key_pem = "invalid_private_key_pem"
    public_key_pem = "invalid_public_key_pem"

    vote = {
        "token": "fjosjfidsw",
        "party_id": 10,
        "election_id": "election_id",
        "candidates_ids": [
            0
        ]
    }

    try:
        electiersa.encrypt_vote(vote, g_private_key_pem, public_key_pem)
    except:
        assert True
