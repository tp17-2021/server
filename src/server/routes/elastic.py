import json
import glob
import base64
import string
import random

import random
import string
import requests
import time
import os
from pprint import pprint

import traceback
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from src.server import config as c
from src.server import schemas
from src.server.database import DB, get_database
from src.server.database import get_parties_with_candidates, get_max_id
import asyncio

from elasticsearch import Elasticsearch, helpers

# Main elastic search connction
ES = Elasticsearch(hosts= [{"scheme": "http", 'host': os.environ['ELASTIC_HOST'],'port': int(os.environ['ELASTIC_PORT'])}])

# Create FastAPI router
router = APIRouter(
    prefix = "/elastic",
    tags = ["Elastic search"],
)

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
            resp = requests.get(uri, headers=headers, json=json_data)
        elif method.lower() == "post":
            resp = requests.post(uri, headers=headers, json=json_data)
        elif method.lower() == "put":
            resp = requests.put(uri, headers=headers, json=json_data)
        elif method.lower() == "delete":
            resp = requests.delete(uri, headers=headers, json=json_data)

        # read the text object string
        try:
            resp_text = json.loads(resp.text)
        except Exception as e:
            resp_text = resp.text

        # catch exceptions and print errors to terminal
    except Exception as error:
        print ('\nelasticsearch_curl() error:', error)
        resp_text = error

    # return the Python dict of the request
    print ("resp_text:", resp_text)
    return resp_text

# helper function for bulk import, inserts index name into object,
def bulk_insert_documents(index, data):

    start_time = time.time()
    count = len(data)
    
    for row in data:
        row["_index"] = index

    res = helpers.bulk(ES, data)
    print(f"Inserted {count} documents. Took {round(time.time() - start_time,3)} s")
    return res


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
            uri='/votes/',
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
                    "administrative_area_name": {
                        "type": "keyword"
                    },
                    "county_name": {
                        "type": "keyword"
                    },
                    "region_name": {
                        "type": "keyword"
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
# TODO spravit menej dopytov najlepsie 1
# TODO check if inserted correctly
# TODO spravit statistiku pre candidates https://stackoverflow.com/questions/34043808/terms-aggregation-for-nested-field-in-elastic-search/34047463
# https://stackoverflow.com/questions/44779794/elastic-search-group-by-multiple-fields-with-filter

@router.post("/synchronize-votes-es", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def synchronize_votes_ES():
    """
    Batch synchronization of votes from Mongo DB to Elastic search 3 Node cluster. Shuld be called in specific intervals during election period.
    """

    if not ES.ping():
        raise ValueError("Connection to ES failed")

    DB  = await get_database()

    # get bulk votes that are not synced
    unsynced_votes = [vote async for vote in DB.votes.aggregate([
        { '$match': {
            'synchronized': None
        }
        }, {
            '$limit': c.ES_SYNCHRONIZATION_BATCH_SIZE
        }
    ])]

    # insert them to ES
    data = []
    for vote in unsynced_votes:

        polling_place_id = vote["polling_place_id"]

        candidates = []
        for candidate_id in vote["candidates_ids"]:

            candidate_data = await DB.candidates.find_one({"_id": candidate_id})

            name = f'{candidate_data["first_name"]} {candidate_data["last_name"]}'
            name = candidate_data["degrees_before"] + " " + name if len(candidate_data["degrees_before"]) else name
            candidates.append({
                "id" : str(candidate_id),
                "fullname" : name,
                "number" : int(candidate_data["order"])
            })

        
        party_data = await DB.parties.find_one({"_id": vote["party_id"]})
        polling_place_data = await DB.polling_places.find_one({"_id": polling_place_id})

        vote_data = {   
            "id" : str(vote["_id"]),
            "token" : vote["token"],
            "election_id": vote["election_id"],
            "date" : int(time.time()),
            "party" : {
                "id" : str(vote["party_id"]),
                "name" : party_data["name"]
            },
            "polling_place": {
                "id" : str(polling_place_id),
                "municipality_name" : polling_place_data["municipality_name"],
                "administrative_area_name": polling_place_data["administrative_area_name"],
                "county_name" : polling_place_data["county_name"],
                "region_name" : polling_place_data["region_name"]
            },
            "candidates": candidates
        }
        data.append(vote_data)

    if len(data):    
        bulk_insert_documents("votes", data)

        # update synced votes state
        unsynced_votes_ids = [ vote["_id"] for vote in unsynced_votes]
        await DB.votes.update_many(
            { 
                "_id" : {
                    "$in" : unsynced_votes_ids
                }
            },
            { "$set": { "synchronized": True }},
        )

    message = f"{len(data)} votes were successfully synchronized" if len(data) else f"No more votes available for synchronization"
    content = {
        "status": "success",
        "message": message
    }

    return content

# TODO change response schema
@router.post("/get-parties-results", status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def get_parties_results():
    request_body = {
        "size": 0,
        "aggs": {
            "agg_by_party": {
                "terms": {
                    "field": "party.name"
                },
                "aggs": {
                    "agg_by_candidate": {
                        "nested": {
                            "path": "candidates"
                        },
                        "aggs": {
                            "candidates": {
                                "terms": {
                                    "size": 1000,
                                    "field": "candidates.fullname"
                                }
                            }
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

    return response

# TODO change response schema
@router.post("/get-party-candidates-results", status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def get_parties_with_candidates_results():
    request_body = {
        "size": 0,
        "aggs": {
            "agg_by_party": {
                "terms": {
                    "field": "party.name"
                },
                "aggs": {
                    "agg_by_candidate": {
                        "nested": {
                            "path": "candidates"
                        },
                        "aggs": {
                            "candidates": {
                                "terms": {
                                    "size": 1000,
                                    "field": "candidates.fullname"
                                }
                            }
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
    print(type(response))
    return response

# TODO change response schema
@router.post("/get-candidates-results", status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def get_candidates_results():
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
                            "size": 100000,
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

    return response

# TODO filterable route by locality, party or pollling place
@router.post("/get-results-by-locality", status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}, 500: {"model": schemas.Message}})
async def get_results_by_locality():
    request_body = {
        "size": 0,
        "aggs": {
            "agg_by_party": {
                "terms": {
                    "field": "party.name"
                },
                "aggs": {
                    "agg_by_candidate": {
                        "nested": {
                            "path": "candidates"
                        },
                        "aggs": {
                            "candidates": {
                                "terms": {
                                    "size": 1000,
                                    "field": "candidates.fullname"
                                }
                            }
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

    return response