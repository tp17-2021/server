# from motor.motor_asyncio import AsyncIOMotorClient
# import pytest

# @pytest.mark.asyncio
# async def test_using_motor_client(motor_client: AsyncIOMotorClient) -> None:
#     """This test has access to a Motor client."""
#     await motor_client.server_info()

# import pytest
# from fastapi.testclient import TestClient

# from src.server.app import app

# @pytest.fixture(scope="module")
# def test_app():
#     client = TestClient(app)
#     yield client  # testing happens here

# def test_root(test_app):
#     response = test_app.get("/")
#     assert response.status_code == 200

import random
import json
import string


from tests import test_env
import os
from unittest import mock 

with mock.patch.dict(os.environ, test_env.envs):
    from src.server.app import app
    from src.server.database import DB

# from src.server.database import DB

# from urllib import response
from fastapi.testclient import TestClient

import pytest
# from httpx import AsyncClient

# from src.server.app import app

import asyncio

client = TestClient(app)



# print(client)


# @pytest.mark.asyncio
# async def test_get():
#     async with AsyncClient(app=app, base_url="http://test") as ac:
#         response = await ac.get("/database/schema")

#     print(response)
#     assert response.status_code == 200



# @pytest.fixture
# def event_loop():
#     yield asyncio.get_event_loop()

# def pytest_sessionfinish(session, exitstatus):
#     asyncio.get_event_loop().close()




@pytest.mark.asyncio
async def test_get():
    # response = client.get("/")
    # print(response.json())
    # assert response.status_code == 200

    votes = [vote async for vote in DB.votes.find()]
    # print(DB)

    # votes = [vote async for vote in DB.votes.find()]
    print(votes)

    assert True


# @pytest.mark.asyncio
# async def test_get2():
#     # response = client.get("/")
#     # print(response.json())
#     # assert response.status_code == 200

#     votes = [vote async for vote in DB.votes.find()]
#     # print(DB)

#     # votes = [vote async for vote in DB.votes.find()]
#     print(votes)

#     assert True


# def test_vote_endpoint_invalid_party_id():
#     DB.votes.drop()

#     data = {
#         "votes": [
#             {
#                 "token": "token1",
#                 "candidates": [
#                     {
#                         "candidate_id": "candidate_id1"
#                     },
#                     {
#                         "candidate_id": "candidate_id2"
#                     }
#                 ],
#                 "party_id": "non_existing_party_id",
#                 "election_id": "election_id1",
#                 "office_id": "office_id1"
#             }
#         ],
#         "office_id": "123456"
#     }

#     response = client.post("/elections/vote", json=data)
#     assert response.status_code == 200

#     # TODO zistit ako spravit databazovy count
#     votes = list(DB.votes.find({}))
#     vote_count  = len(votes)

#     assert vote_count == 1


# def test_vote_endpoint_vote_is_inserted():
#     # count votes after 1 insert in DB (successful vote)

#     DB.votes.drop()

#     data = {
#         "votes": [
#             {
#                 "token": "token1",
#                 "candidates": [
#                     {
#                         "candidate_id": "candidate_id1"
#                     },
#                     {
#                         "candidate_id": "candidate_id2"
#                     }
#                 ],
#                 "party_id": "party_id1",
#                 "election_id": "election_id1",
#                 "office_id": "office_id1"
#             }
#         ],
#         "office_id": "123456"
#     }

#     response = client.post("/elections/vote", json=data)
#     assert response.status_code == 200

#     # TODO
#     # figure out how to make DB count
#     votes = list(DB.votes.find({}))
#     vote_count  = len(votes)

#     assert vote_count == 1
