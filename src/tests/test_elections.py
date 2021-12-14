from src.server.app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_vote_endpoint_good_request():
    # success vote
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