# from src.server.app import app
# from fastapi.testclient import TestClient

# client = TestClient(app)


# def test_vote_endpoint_invalid_request():
#     # mising body
#     response = client.post("/elections/vote")
#     assert response.status_code == 422


# def test_vote_endpoint_missing_attributes():
#     # missing atribute in request
#     data = {
#         "office_id": ""
#     }

#     response = client.post("/elections/vote", json=data)
#     assert response.status_code == 422



# def test_vote_endpoint_invalid_request():
#     # incorrect field in request
#     data = {
#         "asd": "",
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
#             },
#             {
#                 "token": "token2",
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
#                 ],
#         "office_id": ""
#     }

#     response = client.post("/elections/vote", json=data)
#     assert response.status_code == 422