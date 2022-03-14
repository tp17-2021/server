import nest_asyncio
nest_asyncio.apply()
__import__('IPython').embed()

import os
import pytest
import asyncio
import requests
from pprint import pprint

import os
import motor.motor_asyncio

from unittest import mock
from tests import envs

with mock.patch.dict(os.environ, envs.envs):
    from src.server.app import app

from src.server.database import connect_to_mongo
from fastapi.testclient import TestClient

client = TestClient(app)

def connect_to_db():
    clinet = motor.motor_asyncio.AsyncIOMotorClient(
        f"{os.environ['SERVER_DB_HOST']}:{os.environ['SERVER_DB_PORT']}"
    )
    db = clinet[os.environ["SERVER_DB_NAME"]]
    _ = str(db)
    return db

@pytest.mark.asyncio
async def test_elastic_nodes_running():
    """
    Check if all 3 ES nodes are running
    """
    # db = await get_database()
    # asyncio.get_event_loop().run_until_complete(connect_to_mongo())

    elastic_url = f"http://{os.environ['ELASTIC_HOST']}:{os.environ['ELASTIC_PORT']}"
    aa = f"{elastic_url}/_cluster/health"
    res = requests.get(aa)
    assert res.status_code == 200
    assert res.json()['status'] == "green"


@pytest.mark.asyncio
async def test_setup_elastic_votes_index():
    """
    Check if setup endpoints completes successfully
    """
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = client.post(
        "/elastic/setup-elastic-vote-index", headers=headers, json={})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_seed_and_synchronize_elastic_vote():
    """
    Try to seed some votes and synchronize them
    """
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    number_of_votes_to_seed = 5

    # Import data
    response = client.post(
        f"/database/import-data", headers=headers, json={})
    assert response.status_code == 200

    # Reset ES ans setup index
    response = client.post(
        "/elastic/setup-elastic-vote-index", headers=headers, json={})
    assert response.status_code == 200

    # Get election status, there should not be any synced votes
    response = client.get(
        "/elastic/elections-status", headers=headers, json={})
    response = response.json()

    votes_in_db = response['data']['total_votes']

    assert response['data']['votes_synchronized_in_elastic'] == 0
    assert response['data']['votes_synchronized_in_db'] == 0

    # Seed 5 votes
    response = client.post(
        f"/database/seed-votes?number_of_votes={number_of_votes_to_seed}", headers=headers, json={})
    assert response.status_code == 200

    # Synchronize new votes
    response = client.post(
        "/elastic/synchronize-votes-es", headers=headers, json={})
    assert response.status_code == 200

    # Get election status, there should be new votes synched
    response = client.get(
        "/elastic/elections-status", headers=headers, json={})
    response = response.json()
    votes_in_db_after_sync = response['data']['total_votes']
    assert votes_in_db_after_sync == votes_in_db + number_of_votes_to_seed


@pytest.mark.run(after='test_seed_and_synchronize_elastic_vote')
@pytest.mark.asyncio
async def test_elestic_statistics():
    """
    Check if elastic statistics enpoints work
    """
    asyncio.get_event_loop().run_until_complete(connect_to_mongo())
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    # Parties results without filter
    response = client.post(
        "/elastic/get-parties-results", headers=headers, json={})
    assert response.status_code == 200

    # Parties results with filter
    response = client.post(
        "/elastic/get-parties-results", headers=headers, json={
            "party": "SME RODINA"
        })
    assert response.status_code == 200

    # Parties and candidates results without filter
    response = client.post(
        "/elastic/get-party-candidate-results", headers=headers, json={})
    assert response.status_code == 200

    # Parties and candidates results with filter
    response = client.post(
        "/elastic/get-party-candidate-results", headers=headers, json={
            "party": "SME RODINA"
        })
    assert response.status_code == 200

    # Parties and candidates results with filter
    response = client.post(
        "/elastic/get-party-candidate-results", headers=headers, json={
            "party": "SME RODINA"
        })
    assert response.status_code == 200

    # Candidates results
    response = client.post(
        "/elastic/get-candidates-results", headers=headers, json={})
    assert response.status_code == 200

    # Get results by locality (Custom region)
    response = client.post(
        "/elastic/get-results-by-locality", headers=headers, json={
            "filter_by": "region_name",
            "filter_value": "Prešovský kraj"
        })
    assert response.status_code == 200
