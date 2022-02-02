# from fastapi.testclient import TestClient
# from src.server.app import app

# client = TestClient(app)

# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200

    
# # def test_vote_endpoint_good_request():
#     # success vote
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



@pytest.fixture
def event_loop():
    yield asyncio.get_event_loop()

def pytest_sessionfinish(session, exitstatus):
    asyncio.get_event_loop().close()

@pytest.mark.asyncio
async def test_get2():
    # response = client.get("/")
    # print(response.json())
    # assert response.status_code == 200

    votes = [vote async for vote in DB.votes.find()]
    # print(DB)

    # votes = [vote async for vote in DB.votes.find()]
    print(votes)

    assert True