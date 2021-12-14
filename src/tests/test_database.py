from src.server.app import app
from src.server.database import DB
from fastapi.testclient import TestClient

client = TestClient(app)


def test_vote_endpoint_invalid_party_id():
    DB.votes.drop()

    data = {
        "votes": [
            {
                "token": "token1",
                "candidates": [
                    {
                        "candidate_id": "candidate_id1"
                    },
                    {
                        "candidate_id": "candidate_id2"
                    }
                ],
                "party_id": "non_existing_party_id",
                "election_id": "election_id1",
                "office_id": "office_id1"
            }
        ],
        "office_id": "123456"
    }

    response = client.post("/elections/vote", json=data)
    assert response.status_code == 200

    # TODO zistit ako spravit databazovy count
    votes = list(DB.votes.find({}))
    vote_count  = len(votes)

    assert vote_count == 1


def test_vote_endpoint_vote_is_inserted():
    # count votes after 1 insert in DB (successful vote)

    DB.votes.drop()

    data = {
        "votes": [
            {
                "token": "token1",
                "candidates": [
                    {
                        "candidate_id": "candidate_id1"
                    },
                    {
                        "candidate_id": "candidate_id2"
                    }
                ],
                "party_id": "party_id1",
                "election_id": "election_id1",
                "office_id": "office_id1"
            }
        ],
        "office_id": "123456"
    }

    response = client.post("/elections/vote", json=data)
    assert response.status_code == 200

    # TODO
    # figure out how to make DB count
    votes = list(DB.votes.find({}))
    vote_count  = len(votes)

    assert vote_count == 1
