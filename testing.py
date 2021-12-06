import os
print(os.getcwd())

from fastapi.testclient import TestClient
from src.server.app import app
from src.server import schemas

client = TestClient(app)


# TODO k testovaniu
# pripojit sa k test databaze ...
# spustanie vsetkzch testov pomocou pytest automaticky
# fixnut cestu src main (chceme testy dat do server priecinku server/tests/...) -> potom v dockerfile zrusit kopirovanie

# Návrhy na testy
# 1. dá sa poslať vote? dojde spravna response a status? 
# 2. ulozil sa poslanay vote?
# 3. poslat par votov a overit vysledok volieb
# 4. existuje configuracny a obsahuje candidatov partiesa a texty?
# 

# pytest testing.py --verbose


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    # assert response.json() == {"msg": "Hello World"}

# ziadne body -> error 422
def test_vote_endpoint_invalid_request():
    response = client.post("/elections/vote")
    assert response.status_code == 422

# zly field ktorz neni v scheme -> error 422
def test_vote_endpoint_invalid_request():
    data = {
        "asd": "",
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
                    },
                    {
                        "token": "token2",
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
        "office_id": ""
    }

    response = client.post("/elections/vote", json=data)
    assert response.status_code == 422

#  -> error 422
def test_vote_endpoint_missing_attributes():
    data = {
        "office_id": ""
    }

    response = client.post("/elections/vote", json=data)
    assert response.status_code == 422

#  success vote test
def test_vote_endpoint_good_request():
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