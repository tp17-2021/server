import os
import pytest
import asyncio

from unittest import mock 
from tests import envs

from rsaelectie import rsaelectie

with mock.patch.dict(os.environ, envs.envs):
    from src.server.app import app
    from src.server.database import DB

from httpx import AsyncClient


@pytest.fixture
def event_loop():
    yield asyncio.get_event_loop()


@pytest.mark.asyncio
async def test_vote_valid_data():
    """
    Everything is valid: public_key_pem, polling_place_id, token, party_id, election_id, candidates_ids
    """

    key_pair = [key_pair async for key_pair in DB.key_pairs.find()][0]
    public_key_pem = key_pair["public_key_pem"]
    polling_place_id = key_pair["polling_place_id"]


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

    encrypted_vote = await rsaelectie.encrypt_vote(public_key_pem, vote)

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "polling_place_id": polling_place_id,
        "votes": [
            encrypted_vote,
        ]
    }

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/elections/vote", headers=headers, json=payload)
        assert response.status_code == 200


# @pytest.mark.asyncio
# async def test_vote_invalid_token():
#     """
#     Invalid token: already in database
#     """

#     key_pair = [key_pair async for key_pair in DB.key_pairs.find()][0]
#     public_key_pem = key_pair["public_key_pem"]
#     polling_place_id = key_pair["polling_place_id"]


#     vote = {
#         "token": "eggc0tddwl",
#         "party_id": 10,
#         "election_id": "election_id",
#         "candidates_ids": [
#             1075,
#             1076,
#             1077
#         ]
#     }

#     encrypted_vote = await rsaelectie.encrypt_vote(public_key_pem, vote)

#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "polling_place_id": polling_place_id,
#         "votes": [
#             encrypted_vote,
#         ]
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/elections/vote", headers=headers, json=payload)
#         assert response.status_code == 400


# @pytest.mark.asyncio
# async def test_vote_invalid_party_id():
#     """
#     Invalid party id: no occurrence in database
#     """

#     key_pair = [key_pair async for key_pair in DB.key_pairs.find()][0]
#     public_key_pem = key_pair["public_key_pem"]
#     polling_place_id = key_pair["polling_place_id"]


#     vote = {
#         "token": "fjosjfidsw",
#         "party_id": -1,
#         "election_id": "election_id",
#         "candidates_ids": [
#             1075,
#             1076,
#             1077
#         ]
#     }

#     encrypted_vote = await rsaelectie.encrypt_vote(public_key_pem, vote)

#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "polling_place_id": polling_place_id,
#         "votes": [
#             encrypted_vote,
#         ]
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/elections/vote", headers=headers, json=payload)
#         assert response.status_code == 400

# @pytest.mark.asyncio
# async def test_vote_invalid_election_id():
#     """
#     Invalid election id: no match
#     """

#     key_pair = [key_pair async for key_pair in DB.key_pairs.find()][0]
#     public_key_pem = key_pair["public_key_pem"]
#     polling_place_id = key_pair["polling_place_id"]


#     vote = {
#         "token": "fjosjfidsw",
#         "party_id": 10,
#         "election_id": "no_match_election_id",
#         "candidates_ids": [
#             1075,
#             1076,
#             1077
#         ]
#     }

#     encrypted_vote = await rsaelectie.encrypt_vote(public_key_pem, vote)

#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "polling_place_id": polling_place_id,
#         "votes": [
#             encrypted_vote,
#         ]
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/elections/vote", headers=headers, json=payload)
#         assert response.status_code == 400


# @pytest.mark.asyncio
# async def test_vote_more_than_5_candidates():
#     """
#     Invalid candidates: more than 5
#     """

#     key_pair = [key_pair async for key_pair in DB.key_pairs.find()][0]
#     public_key_pem = key_pair["public_key_pem"]
#     polling_place_id = key_pair["polling_place_id"]


#     vote = {
#         "token": "fjosjfidsw",
#         "party_id": 10,
#         "election_id": "election_id",
#         "candidates_ids": [
#             1075,
#             1076,
#             1077,
#             1078,
#             1079,
#             1080
#         ]
#     }

#     encrypted_vote = await rsaelectie.encrypt_vote(public_key_pem, vote)

#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "polling_place_id": polling_place_id,
#         "votes": [
#             encrypted_vote,
#         ]
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/elections/vote", headers=headers, json=payload)
#         assert response.status_code == 400


# @pytest.mark.asyncio
# async def test_vote_duplicate_candidates():
#     """
#     Invalid candidates: duplicate ids
#     """

#     key_pair = [key_pair async for key_pair in DB.key_pairs.find()][0]
#     public_key_pem = key_pair["public_key_pem"]
#     polling_place_id = key_pair["polling_place_id"]


#     vote = {
#         "token": "fjosjfidsw",
#         "party_id": 10,
#         "election_id": "election_id",
#         "candidates_ids": [
#             1075,
#             1075
#         ]
#     }

#     encrypted_vote = await rsaelectie.encrypt_vote(public_key_pem, vote)

#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "polling_place_id": polling_place_id,
#         "votes": [
#             encrypted_vote,
#         ]
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/elections/vote", headers=headers, json=payload)
#         assert response.status_code == 400


# @pytest.mark.asyncio
# async def test_vote_invalid_candidate_id():
#     """
#     Invalid candidate id: no occurrence in database
#     """

#     key_pair = [key_pair async for key_pair in DB.key_pairs.find()][0]
#     public_key_pem = key_pair["public_key_pem"]
#     polling_place_id = key_pair["polling_place_id"]


#     vote = {
#         "token": "fjosjfidsw",
#         "party_id": 10,
#         "election_id": "election_id",
#         "candidates_ids": [
#             -1
#         ]
#     }

#     encrypted_vote = await rsaelectie.encrypt_vote(public_key_pem, vote)

#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "polling_place_id": polling_place_id,
#         "votes": [
#             encrypted_vote,
#         ]
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/elections/vote", headers=headers, json=payload)
#         assert response.status_code == 400


# @pytest.mark.asyncio
# async def test_vote_invalid_candidate_id2():
#     """
#     Invalid candidate id: wrong id for entered party id
#     """

#     key_pair = [key_pair async for key_pair in DB.key_pairs.find()][0]
#     public_key_pem = key_pair["public_key_pem"]
#     polling_place_id = key_pair["polling_place_id"]


#     vote = {
#         "token": "fjosjfidsw",
#         "party_id": 10,
#         "election_id": "election_id",
#         "candidates_ids": [
#             0
#         ]
#     }

#     encrypted_vote = await rsaelectie.encrypt_vote(public_key_pem, vote)

#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "polling_place_id": polling_place_id,
#         "votes": [
#             encrypted_vote,
#         ]
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/elections/vote", headers=headers, json=payload)
#         assert response.status_code == 400


# @pytest.mark.asyncio
# async def test_vote_invalid_candidate_id2():
#     """
#     Invalid candidate id: wrong id for entered party id
#     """

#     key_pair = [key_pair async for key_pair in DB.key_pairs.find()][0]
#     public_key_pem = key_pair["public_key_pem"]
#     polling_place_id = key_pair["polling_place_id"]


#     vote = {
#         "token": "fjosjfidsw",
#         "party_id": 10,
#         "election_id": "election_id",
#         "candidates_ids": [
#             0
#         ]
#     }

#     encrypted_vote = await rsaelectie.encrypt_vote(public_key_pem, vote)

#     headers = {
#         "accept": "application/json",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "polling_place_id": polling_place_id,
#         "votes": [
#             encrypted_vote,
#         ]
#     }

#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.post("/elections/vote", headers=headers, json=payload)
#         assert response.status_code == 400