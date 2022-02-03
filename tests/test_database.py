# import os
# import pytest
# import asyncio

# from unittest import mock
# from tests import envs

# with mock.patch.dict(os.environ, envs.envs):
#     from src.server.app import app
#     from src.server.database import DB


# @pytest.fixture
# def event_loop():
#     yield asyncio.get_event_loop()


# @pytest.mark.asyncio
# async def test_get_party_by_id():
#     """
#     Get collection with party id equals 0
#     """

#     party = [collection async for collection in DB.parties.find()][0]

#     assert party == {
#         "_id" : 0,
#         "party_number" : 1,
#         "name" : "Slovenská ľudová strana Andreja Hlinku",
#         "abbreviation" : "Slovenská ľudová strana (SĽS)",
#         "image" : "slovenska-ludova-strana-andreja-hlinku.png",
#     }


# @pytest.mark.asyncio
# async def test_get_candidate_by_id():
#     """
#     Get collection with candidate id equals 0
#     """

#     candidate = [collection async for collection in DB.candidates.find()][0]

#     assert candidate == {
#         "_id" : 0,
#         "party_number" : 1,
#         "order" : 1,
#         "first_name" : "Jozef",
#         "last_name" : "Sásik",
#         "degrees_before" : "Ing.",
#         "age" : 61,
#         "occupation" : "predseda SĽS Andreja Hlinku",
#         "residence" : "Banská Bystrica",
#     }


# @pytest.mark.asyncio
# async def test_get_polling_place_by_id():
#     """
#     Get collection with polling place id equals 0
#     """

#     polling_place = [collection async for collection in DB.polling_places.find()][0]

#     assert polling_place == {
#         "_id" : 0,
#         "region_code" : 1,
#         "region_name" : "Bratislavský kraj",
#         "administrative_area_code" : 101,
#         "administrative_area_name" : "Bratislava",
#         "county_code" : 101,
#         "county_name" : "Bratislava I",
#         "municipality_code" : 528595,
#         "municipality_name" : "Bratislava - Staré Mesto",
#         "polling_place_number" : 1,
#         "registered_voters_count" : 1234,
#     }


# @pytest.mark.asyncio
# async def test_get_vote_by_id():
#     """
#     Get collection with votes id equals 0
#     """

#     vote = [collection async for collection in DB.votes.find()][0]

#     assert vote == {
#         "_id" : 0,
#         "token" : "nr1waa4uhx",
#         "party_id" : 22,
#         "election_id" : "election_id",
#         "candidates_ids" : [
#             2431
#         ],
#         "polling_place_id" : 4640,
#     }


# @pytest.mark.asyncio
# async def test_insert_vote():
#     """
#     Insert one vote and check if number of all votes has increased by one 
#     """

#     before_insert_ids = [collection["_id"] async for collection in DB.votes.find({}, {"_id":1})]
#     before_insert_ids.sort()
#     max_id = before_insert_ids[-1]

#     vote_to_be_inserted = {
#         "_id" : max_id + 1,
#         "token" : "abcefghijk",
#         "party_id" : 0,
#         "election_id" : "election_id",
#         "candidates_ids" : [
#             0,
#             1,
#             2,
#             3,
#             4
#         ],
#         "polling_place_id" : 0,
#     }

#     await DB.votes.insert_one(vote_to_be_inserted)

#     after_insert_ids = [collection["_id"] async for collection in DB.votes.find({}, {"_id":1})]

#     assert len(before_insert_ids) + 1 == len(after_insert_ids)