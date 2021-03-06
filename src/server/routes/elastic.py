import json
import glob
import base64
import string
import random
import math
from collections import OrderedDict

import random
import string
import requests
import time
import os
from pprint import pprint

import traceback
from fastapi import status, APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from src.server import config as c
from src.server import schemas
from src.server.database import DB, get_database
from src.server.database import get_parties_with_candidates, get_max_id
from src.server.routes.auth import *
import asyncio

from elasticsearch import Elasticsearch, helpers

# Results status
results_published = False

# Main elastic search connction
ES = Elasticsearch(hosts=[{"scheme": "http", 'host': os.environ['ELASTIC_HOST'], 'port': int(
    os.environ['ELASTIC_PORT'])}])

# Create FastAPI router
router = APIRouter(
    prefix="/elastic",
    tags=["Elastic search"],
)


def check_elastic_is_running():
    global ES
    if not ES.ping():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Elastic is not available yet")
        # return False
        # raise ValueError("Connection failed")

    if not ES.indices.exists(index="votes"):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="Elastic votes index was not created yet")
    return True

# function for the cURL requests to Elastic search


def elasticsearch_curl(uri='', method='get', json_data=''):

    uri = f"http://{os.environ['ELASTIC_HOST']}:{os.environ['ELASTIC_PORT']}{uri}"

    # pass header option for content type if request has a
    # body to avoid Content-Type error in Elasticsearch v6.0
    headers = {
        'Content-Type': 'application/json',
    }

    try:
        # make HTTP method parameter case-insensitive by converting to lower()
        if method.lower() == "get":
            if(json_data != None):
                resp = requests.get(uri, headers=headers, json=json_data)
            else:
                resp = requests.get(uri, headers=headers)
        elif method.lower() == "post":
            resp = requests.post(uri, headers=headers, json=json_data)
        elif method.lower() == "put":
            resp = requests.put(uri, headers=headers, json=json_data)
        elif method.lower() == "delete":
            resp = requests.delete(uri, headers=headers)

        # read the text object string
        try:
            resp_text = json.loads(resp.text)
        except Exception as e:
            resp_text = resp.text

        # catch exceptions and print errors to terminal
    except Exception as error:
        print('\nelasticsearch_curl() error:', error)
        resp_text = error

    # return the Python dict of the request
    # print("resp_text:", resp_text)
    return resp_text

# helper function for bulk import, inserts index name into object,


def bulk_insert_documents(index, data):

    start_time = time.time()
    count = len(data)

    for row in data:
        row["_index"] = index

    res = helpers.bulk(ES, data)
    print(
        f"Inserted {count} documents. Took {round(time.time() - start_time,3)} s")
    return res


def check_results_published():
    global results_published
    return results_published == True

@router.post("/results/publish")
def results_publish(current_user: User = Depends(get_current_active_user)):
    global results_published
    results_published = True
    content = {
        "status": "success",
        "message": "Voting results published"
    }

    return content

@router.post("/results/hide")
def results_publish(current_user: User = Depends(get_current_active_user)):
    global results_published
    results_published = False
    content = {
        "status": "success",
        "message": "Voting results hidden"
    }

    return content

@router.get("/results/status")
def results_status():
    global results_published
    content = {
        "published": results_published
    }

    return content


@router.post("/setup-elastic-vote-index", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def setup_elastic_votes_index():
    """
    Setup elastic search. Drop index if previously used. Create new index and variables mapping.
    """

    if not ES.ping():
        raise ValueError("Connection to ES failed")

    # Drop index if exists
    # -------------------------------------------------------------------------
    response = elasticsearch_curl(
        uri='/votes/?ignore_unavailable=true',
        method='delete'
    )

    if("acknowledged" not in response or response["acknowledged"] != True):
        raise Exception("Delete index failed")

    # Create votes index
    # -------------------------------------------------------------------------
    request_body = {
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 0
        }
    }

    response = elasticsearch_curl(
        uri='/votes',
        method='put',
        json_data=request_body
    )
    if("acknowledged" not in response or response["acknowledged"] != True):
        raise Exception("Create index failed")

    # Create mapping
    # -------------------------------------------------------------------------
    request_body = {
        "dynamic": "strict",
        "properties": {
            "id": {
                "type": "keyword"
            },
            "token": {
                "type": "keyword"
            },
            "election_id": {
                "type": "keyword"
            },
            "date": {
                "type": "date"
            },
            "party": {
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "keyword"
                    }
                }
            },
            "polling_place": {
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "municipality_name": {
                        "type": "keyword"
                    },
                    "municipality_code": {
                        "type": "long"
                    },
                    "administrative_area_name": {
                        "type": "keyword"
                    },
                    "administrative_area_code": {
                        "type": "long"
                    },
                    "county_name": {
                        "type": "keyword"
                    },
                    "county_code": {
                        "type": "long"
                    },
                    "region_name": {
                        "type": "keyword"
                    },
                    "region_code": {
                        "type": "long"
                    }
                }
            },
            "candidates": {
                "type": "nested",
                "properties": {
                    "id": {
                        "type": "keyword"
                    },
                    "fullname": {
                        "type": "keyword"
                    },
                    "number": {
                        "type": "long"
                    }
                }
            }
        }
    }

    response = elasticsearch_curl(
        uri='/votes/_mapping',
        method='put',
        json_data=request_body
    )
    if("acknowledged" not in response or response["acknowledged"] != True):
        raise Exception("Create mapping failed")

    # If all was successfull, return success
    content = {
        "status": "success",
        "message": f"ES index setup success"
    }
    return content

# TODO run as cron
# TODO database transaction (ATOMIC)
# TODO insertovanie cisla id pre vote nech neni od 1 ale object random id
# TODO check if inserted correctly


@router.post("/synchronize-votes-es", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def synchronize_votes_ES(number=c.ES_SYNCHRONIZATION_BATCH_SIZE):
    """
    Batch synchronization of votes from Mongo DB to Elastic search 3 Node cluster. Shuld be called in specific intervals during election period.
    """

    if not ES.ping():
        raise ValueError("Connection to ES failed")

    DB = await get_database()

    # get bulk votes that are not synced
    unsynced_votes = [vote async for vote in DB.votes.aggregate([
        {
            '$match': {
                'synchronized': None
            }
        }, {
            '$limit': int(number)
        }, {
            '$lookup': {
                'from': 'parties',
                'localField': 'party_id',
                'foreignField': '_id',
                'as': 'party'
            }
        }, {
            '$unwind': {
                'path': '$party',
                'preserveNullAndEmptyArrays': True
            }
        }, {
            '$lookup': {
                'from': 'polling_places',
                'localField': 'polling_place_id',
                'foreignField': '_id',
                'as': 'polling_place'
            }
        }, {
            '$unwind': {
                'path': '$polling_place'
            }
        }, {
            '$lookup': {
                'from': 'candidates',
                'localField': 'candidate_ids',
                'foreignField': '_id',
                'as': 'candidates'
            }
        }
    ])]
    
    # insert them to ES
    data = []
    for vote in unsynced_votes:
        
        is_empty_vote = not "party" in vote
        party = vote["party"] if not is_empty_vote else None # empty votes have party None
        polling_place = vote["polling_place"]
        candidates = []

        for candidate in vote["candidates"]:

            name = f'{candidate["first_name"]} {candidate["last_name"]}'
            name = candidate["degrees_before"] + " " + \
                name if len(candidate["degrees_before"]) else name
            candidates.append({
                "id": str(candidate["_id"]),
                "fullname": name,
                "number": int(candidate["order"])
            })

        if is_empty_vote:
            party_to_insert = None
        else:
            party_to_insert = {
                "id": str(vote["party_id"]),
                "name": party["name"]
            }

        vote_data = {
            "id": str(vote["_id"]),
            "token": vote["token"],
            "election_id": vote["election_id"],
            "date": int(time.time()),
            "party": party_to_insert,
            "polling_place": {
                "id": str(polling_place["_id"]),
                "municipality_name": polling_place["municipality_name"],
                "municipality_code": polling_place["municipality_code"],
                "administrative_area_name": polling_place["administrative_area_name"],
                "administrative_area_code": polling_place["administrative_area_code"],
                "county_name": polling_place["county_name"],
                "county_code": polling_place["county_code"],
                "region_name": polling_place["region_name"],
                "region_code": polling_place["region_code"]
            },
            "candidates": candidates
        }
        data.append(vote_data)

    if len(data):
        bulk_insert_documents("votes", data)

        # update synced votes state
        unsynced_votes_ids = [vote["_id"] for vote in unsynced_votes]
        await DB.votes.update_many(
            {
                "_id": {
                    "$in": unsynced_votes_ids
                }
            },
            {"$set": {"synchronized": True}},
        )

    message = f"{len(data)} votes were successfully synchronized" if len(
        data) else f"No more votes available for synchronization"
    content = {
        "status": "success",
        "message": message
    }

    return content


@router.post("/get-parties-results", status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def get_parties_results(request: schemas.StatisticsPerPartyRequest):

    if(not check_results_published()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results are not published yet")
    check_elastic_is_running()

    DB = await get_database()

    request_body = {
        "size": 0,
        "aggs": {
            "agg_by_party": {
                "terms": {
                    "size": 100,
                    "field": "party.id"
                },
                "aggs": {
                    "agg_by_candidate": {
                        "nested": {
                            "path": "candidates"
                        },
                        "aggs": {
                            "candidates": {
                                "terms": {
                                    "size": c.ELASTIC_RESULTS_LIMIT,
                                    "field": "candidates.id"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    # Filter by one party only
    if(request.party):
        request_body["query"] = {"term": {
            f"party.name": request.party
        }}

    response = elasticsearch_curl(
        uri='/votes/_search',
        method='post',
        json_data=request_body
    )

    transformed_data = []
    total_votes = await DB.votes.count_documents({})
    for party in response['aggregations']['agg_by_party']['buckets']:
        candidates = []

        for candidate in party["agg_by_candidate"]["candidates"]["buckets"]:
            candidates.append({
                "id": candidate["key"],
                "doc_count": candidate["doc_count"],
                "percentage": round(candidate["doc_count"] / total_votes * 100, 4)
            })

        transformed_data.append({
            "id": party["key"],
            "doc_count": party["doc_count"],
            "candidates": candidates,
            "percentage": round(party["doc_count"] / total_votes * 100, 4)
        })

    # calc seats if filter is not used
    if (not request.party):
        transformed_data = calcualte_winning_parties_and_seats(
            transformed_data)

    # remove candidates from response, they are no longer needed (needed only for seats calculation)
    for party in transformed_data:
        if "candidates" in party:
            del party["candidates"]

    return transformed_data


def calcualte_winning_parties_and_seats(transformed_data):
    """
    Find parties having more than 5% (threshold) and count all votes for these parties.
    In case parties have less then threshold value, take all parties
    Calculate relative vote percentage from this set of parties and calculate result seats for each party
    """

    # Find parties having more than 5% (threshold) and count all votes for these parties
    votes_in_winning_parties = 0
    total_votes = 0
    accepted_parties = 0
    seats_taken = 0

    for party in transformed_data:
        total_votes += party["doc_count"]
        if party["percentage"] >= c.PARLIAMENT_ACCEPTANCE_THRESHOLD:
            votes_in_winning_parties += party["doc_count"]
            party["in_parliament"] = True
            accepted_parties += 1
        else:
            party["in_parliament"] = False

    # In case parties have less then threshold value, take all parties
    if(accepted_parties == 0):
        votes_in_winning_parties = total_votes
        for party in transformed_data:
            party["in_parliament"] = True

    # Store diiference between float number of seats based on relative percentage and floored number
    floored_seats_per_party = {}

    # Republic number represents votes needed for one seat
    republic_number = math.floor(
        votes_in_winning_parties / (c.PARLIAMENTS_SEATS_TO_SPLIT + 1))

    # If only few votes in db and republic number is 0, no seats can be given
    if(republic_number == 0):
        return transformed_data

    # Calculate relative vote percentage from this set of parties and calculate result seats for each party
    for party in transformed_data:
        if(not party["in_parliament"]):
            continue

        party["relative_percentage"] = round(
            party["doc_count"] / votes_in_winning_parties * 100, 4)

        party["seats"] = party["doc_count"] // republic_number
        seats_taken += party["seats"]

        # Edge case when 151 seats were allocated hack
        if(seats_taken == (c.PARLIAMENTS_SEATS_TO_SPLIT + 1)):
            party["seats"] -= 1
            seats_taken -= 1

        floored_seats_per_party[party["id"]
                                ] = party["doc_count"] % republic_number

    ordered_floored_seats_per_party = OrderedDict(
        sorted(floored_seats_per_party.items(), key=lambda x: x[1], reverse=True))

    # Not all seats were taken. Remaining seats will be split to the parties with highest remainders after flooring.
    if(seats_taken <= c.PARLIAMENTS_SEATS_TO_SPLIT):

        seats_left = c.PARLIAMENTS_SEATS_TO_SPLIT - seats_taken
        ordered_floored_seats_per_party = OrderedDict(
            sorted(floored_seats_per_party.items(), key=lambda x: x[1], reverse=True))

        # crete list of parties that will have one more seat due to scrutinium
        current_seat = 0
        parties_with_added_seat = []
        for party in ordered_floored_seats_per_party:
            if current_seat == seats_left:
                break
            parties_with_added_seat.append(party)
            current_seat += 1

        # add additional seat and flag
        for party in transformed_data:
            if party["id"] in parties_with_added_seat:
                party["seats"] += 1
                party["additional_seat"] = True

    # Find number of seats that cannot be taken
    unfillable_seats = 0
    parties_eligible_for_reamining_seats = []
    for party in transformed_data:
        if party["in_parliament"]:
            if len(party['candidates']) < party['seats']:
                unfillable_seats += (party['seats'] - len(party['candidates']))
                party['original_seats'] = party['seats']
                party['seats'] = len(party['candidates'])
            else:
                parties_eligible_for_reamining_seats.append(party["id"])

    # Give free seats to parties one by one in order
    if(unfillable_seats > 0):
        while unfillable_seats > 0:
            for party in transformed_data:
                if party["in_parliament"]:
                    if party['id'] in parties_eligible_for_reamining_seats:
                        party['seats'] += 1
                        unfillable_seats -= 1

                        if unfillable_seats <= 0:
                            break

    # Set flag for candidates in parliament
    for party in transformed_data:
        for i, candidate in enumerate(party['candidates']):
            candidate['in_parliament'] = True if 'seats' in party and i < party['seats'] else False

    return transformed_data


@router.post("/get-party-candidate-results", status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def get_parties_with_candidates_results(request: schemas.StatisticsPerPartyRequest):

    if(not check_results_published()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results are not published yet")
    check_elastic_is_running()

    DB = await get_database()

    request_body = {
        "size": 0,
        "aggs": {
            "agg_by_party": {
                "terms": {
                    "size": 100,
                    "field": "party.id"
                },
                "aggs": {
                    "agg_by_candidate": {
                        "nested": {
                            "path": "candidates"
                        },
                        "aggs": {
                            "candidates": {
                                "terms": {
                                    "size": c.ELASTIC_RESULTS_LIMIT,
                                    "field": "candidates.id"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    # Filter by one party only
    if(request.party):
        request_body["query"] = {"term": {
            f"party.name": request.party
        }}

    response = elasticsearch_curl(
        uri='/votes/_search',
        method='post',
        json_data=request_body
    )

    # TODO zjednotit pomenovania agg, aggs, aggretgaiton...
    transformed_data = []
    total_votes = await DB.votes.count_documents({})
    for party in response['aggregations']['agg_by_party']['buckets']:
        candidates = []

        for candidate in party["agg_by_candidate"]["candidates"]["buckets"]:
            candidates.append({
                "id": candidate["key"],
                "doc_count": candidate["doc_count"],
                "percentage": round(candidate["doc_count"] / total_votes * 100, 4)
            })

        transformed_data.append({
            "id": party["key"],
            "doc_count": party["doc_count"],
            "candidates": candidates,
            "percentage": round(party["doc_count"] / total_votes * 100, 4)
        })

    # calc seats if filter is not used
    if (not request.party):
        transformed_data = calcualte_winning_parties_and_seats(
            transformed_data)

    return transformed_data


@router.post("/get-candidates-results", status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def get_candidates_results():

    if(not check_results_published()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results are not published yet")
    check_elastic_is_running()

    DB = await get_database()

    request_body = {
        "size": 0,
        "aggs": {
            "agg_by_candidate": {
                "nested": {
                    "path": "candidates"
                },
                "aggs": {
                    "candidates": {
                        "terms": {
                            "size": c.ELASTIC_RESULTS_LIMIT,
                            "field": "candidates.fullname"
                        }
                    }
                }
            }
        }
    }

    response = elasticsearch_curl(
        uri='/votes/_search',
        method='post',
        json_data=request_body
    )

    transformed_data = []
    total_votes = await DB.votes.count_documents({})

    for candidate in response['aggregations']["agg_by_candidate"]["candidates"]["buckets"]:
        transformed_data.append({
            "name": candidate["key"],
            "doc_count": candidate["doc_count"],
            "percentage": round(candidate["doc_count"] / total_votes * 100, 4)
        })

    return transformed_data


async def get_eligible_voters_per_locality(filter_by=None):

    DB = await get_database()

    # if no filter is provided, then return sum for all polling places
    group_by_clause = f'${filter_by}' if filter_by else ''

    eligible_voters_per_locality_count = [res async for res in DB.polling_places.aggregate([
        {
            '$group': {
                '_id': group_by_clause,  # e.g. '$region_name'
                'registered_voters': {
                    '$sum': '$registered_voters_count'
                }
            }
        }
    ])]

    # return dictionary for each locality of specified group by clause with count of eligible candidates indexed by id
    tmp = {}
    for row in eligible_voters_per_locality_count:
        tmp[str(row['_id'])] = row['registered_voters']
    eligible_voters_per_locality_count = tmp

    return eligible_voters_per_locality_count


@router.get("/get-results-by-locality-mongo")
async def get_results_by_locality_mongo():
    """
    Used to provide benchmark for ES vs Mongo aggregation queries
    """

    if(not check_results_published()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results are not published yet")

    DB = await get_database()
    results = [res async for res in DB.votes.aggregate([
        {
            '$unwind': {
                'path': '$candidate_ids'
            }
        }, {
            '$group': {
                '_id': '$candidate_ids',
                'votes': {
                    '$sum': 1
                }
            }
        }
    ])]

    # pprint(results)
    return results

# TODO add filter specific value


@router.post("/get-results-by-locality", status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def get_results_by_locality(request: schemas.StatisticsPerLocalityRequest):
    check_elastic_is_running()
    DB = await get_database()

    if(not check_results_published()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results are not published yet")

    calculate_candidates_aggs = True if request.filter_value else False
    print("calculate_candidates_aggs", calculate_candidates_aggs)

    eligible_voters_per_locality_count = await get_eligible_voters_per_locality(request.filter_by)

    # TODO doplnenie celych objektov
    # parties_data = await get_parties_with_candidates()

    request_body = {
        "size": 0,
        "aggs": {
            "agg_by_locality": {
                "terms": {
                    "size": c.ELASTIC_RESULTS_LIMIT,
                    "field": "polling_place." + request.filter_by
                },
                "aggs": {
                    "agg_by_party": {
                        "terms": {
                            "size": c.ELASTIC_RESULTS_LIMIT,
                            "field": "party.id"
                        }
                    }
                }
            }
        }
    }

    if calculate_candidates_aggs:
        request_body["aggs"]["agg_by_locality"]["aggs"]["agg_by_party"]["aggs"] = {
            "agg_by_candidate": {
                "nested": {
                    "path": "candidates"
                },
                "aggs": {
                    "candidates": {
                        "terms": {
                            "size": c.ELASTIC_RESULTS_LIMIT,
                            "field": "candidates.fullname"
                        }
                    }
                }
            }
        }

    # Add filter value if provided in request
    if(request.filter_value):
        request_body["query"] = {"term": {
            f"polling_place.{request.filter_by}": request.filter_value
        }}
    
    response = elasticsearch_curl(
        uri='/votes/_search',
        method='post',
        json_data=request_body
    )

    res = response['aggregations']['agg_by_locality']['buckets']
    transformed_data = []

    for row in res:
        parties = []
        locality_votes_total = row['doc_count']
        for party in row["agg_by_party"]["buckets"]:
            candidates = []
            party_votes = party["doc_count"]

            # run only if candidates aggs is available
            if calculate_candidates_aggs:
                for candidate in party["agg_by_candidate"]["candidates"]["buckets"]:
                    candidates.append({
                        "name": candidate["key"],
                        "doc_count": candidate["doc_count"],
                        "percentage": round(candidate["doc_count"] / locality_votes_total * 100, 4)
                    })

            parties.append({
                "id": party["key"],
                "doc_count": party["doc_count"],
                "candidates": candidates,
                "percentage": round(party_votes / locality_votes_total * 100, 4)
            })

        locality = {
            "type": request.filter_by,
            "code": row["key"],
            "doc_count": row["doc_count"],
            "parties": parties,
            "registered_participants": eligible_voters_per_locality_count[str(row["key"])]
        }

        locality["participation"] = round(
            locality["doc_count"] / locality["registered_participants"] * 100, 2)

        transformed_data.append(locality)

    return transformed_data

# TODO pridat percentualnu ucast
# TODO okontrolovat get max id, nechat nech sa id generuje


async def get_parties_and_candidates_lookup():
    lookup = {
        "parties": {},
        "candidates": {}
    }
    data = await get_parties_with_candidates()

    for party in data:

        party_without_candidates = party.copy()
        party_without_candidates.pop("candidates")
        # pprint(party_without_candidates)
        lookup["parties"][party["_id"]] = party_without_candidates

        for candidate in party["candidates"]:
            lookup["candidates"][candidate["_id"]] = candidate

    return lookup

@router.get("/elections-status", status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def get_elections_status(filter_by: str = "", filter_value: str = ""):
    
    # if(not check_results_published()):
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Results are not published yet")
    """
    Used to provide status of elections (number of votes, number of polling places, participation , etc.).
    This can be used in statistics FE app. This endpoints counts votes only in ES, and is therefore faster.
    """
    check_elastic_is_running()

    DB = await get_database()

    response = elasticsearch_curl(
        uri='/votes/_refresh',
        method='post',
        json_data=None
    )

    if(filter_by and filter_value):
        registered_voters = (await get_eligible_voters_per_locality(filter_by))[filter_value]

        elastic_request_data = {
            "size": 0,
            "query": {
                "term": {
                    f"polling_place.{filter_by}": int(filter_value)
                }
            },
            "aggs": {
                "agg_by_locality": {
                    "terms": {
                        "size": 10000,
                        "field": f"polling_place.{filter_by}"
                    }
                }
            }
        }

        response = elasticsearch_curl(
            uri='/votes/_search',
            method='post',
            json_data=elastic_request_data
        )
        votes_synchronized_in_elastic = response["aggregations"]["agg_by_locality"]["buckets"][0]["doc_count"]
        number_of_polling_places = await DB.polling_places.count_documents({f'{filter_by}': int(filter_value)})

    else:
        registered_voters = (await get_eligible_voters_per_locality())['']
        number_of_polling_places = await DB.polling_places.count_documents({})

        response = elasticsearch_curl(
            uri='/votes/_count',
            method='get',
            json_data=None
        )

        votes_synchronized_in_elastic = response['count']

    content = {
        "status": "success",
        "data": {
            "registered_voters": registered_voters,
            "total_votes": votes_synchronized_in_elastic,
            "participation": round(
                votes_synchronized_in_elastic / registered_voters * 100, 2),
            "number_of_polling_places": number_of_polling_places
        }
    }
    return content


@router.get("/synchronization-status", status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def get_synchronization_status(filter_by: str = "", filter_value: str = ""):
    """
    Used to provide status of elections (number of votes, number of polling places, participation, etc.).
    It also provides comparison of number of votes in ES and in DB (both synced and all).
    This can be used for testing purposes but is rather slow.
    """
    check_elastic_is_running()

    DB = await get_database()

    if(filter_by and filter_value):
        registered_voters = (await get_eligible_voters_per_locality(filter_by))[filter_value]

        # pipeline for votes in db in specific locality
        pipeline = [
            {
                '$match': {
                    f'{filter_by}': int(filter_value)
                }
            }, {
                '$lookup': {
                    'from': 'votes',
                    'localField': '_id',
                    'foreignField': 'polling_place_id',
                    'as': 'votes'
                }
            }, {
                '$unwind': {
                    'path': '$votes'
                }
            }, {
                '$count': 'votes'
            }
        ]

        votes_total_in_db = [res async for res in DB.polling_places.aggregate(pipeline)]
        votes_total_in_db = votes_total_in_db[0]['votes']

        pipeline_votes_per_locality_synced = [
            {
                '$match': {
                    f'{filter_by}': int(filter_value)
                }
            }, {
                '$lookup': {
                    'from': 'votes',
                    'localField': '_id',
                    'foreignField': 'polling_place_id',
                    'as': 'votes'
                }
            }, {
                '$unwind': {
                    'path': '$votes'
                }
            }, {
                '$match': {
                    "votes.synchronized": True
                }
            }, {
                '$count': 'votes'
            }
        ]

        votes_synchronized_in_db = [res async for res in DB.polling_places.aggregate(pipeline_votes_per_locality_synced)]
        votes_synchronized_in_db = votes_synchronized_in_db[0]['votes']

        elastic_request_data = {
            "size": 0,
            "query": {
                "term": {
                    f"polling_place.{filter_by}": int(filter_value)
                }
            },
            "aggs": {
                "agg_by_locality": {
                    "terms": {
                        "size": 10000,
                        "field": f"polling_place.{filter_by}"
                    }
                }
            }
        }

        response = elasticsearch_curl(
            uri='/votes/_search',
            method='post',
            json_data=elastic_request_data
        )

        number_of_polling_places = await DB.polling_places.count_documents({f'{filter_by}': int(filter_value)})

        votes_synchronized_in_elastic = response["aggregations"]["agg_by_locality"]["buckets"][0]["doc_count"]
    else:
        registered_voters = (await get_eligible_voters_per_locality())['']
        number_of_polling_places = await DB.polling_places.count_documents({})
        votes_total_in_db = await DB.votes.count_documents({})
        votes_synchronized_in_db = await DB.votes.count_documents({"synchronized": True})

        response = elasticsearch_curl(
            uri='/votes/_refresh',
            method='post',
            json_data=None
        )

        response = elasticsearch_curl(
            uri='/votes/_count',
            method='get',
            json_data=None
        )

        votes_synchronized_in_elastic = response['count']

    content = {
        "status": "success",
        "data": {
            "registered_voters": registered_voters,
            "total_votes": votes_total_in_db,
            "participation": round(
                votes_total_in_db / registered_voters * 100, 2),
            "votes_synchronized_in_db": votes_synchronized_in_db,
            "votes_synchronized_in_elastic": votes_synchronized_in_elastic,
            "number_of_polling_places": number_of_polling_places
        }
    }
    return content
