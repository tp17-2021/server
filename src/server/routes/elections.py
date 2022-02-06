import json
import glob
import base64
import string
import random
from pytest import yield_fixture

from electiersa import electiersa

import traceback
from fastapi import status, APIRouter
from fastapi.responses import JSONResponse

from src.server import config
from src.server import schemas
from src.server.database import DB, get_database
from src.server.database import get_parties_with_candidates, get_max_id
import asyncio

# Create FastAPI router
router = APIRouter(
    prefix = "/elections",
    tags = ["Elections"],
)


async def validate_polling_place_id(polling_place_id):
    DB  = await get_database()

    if await DB.key_pairs.count_documents({"polling_place_id":polling_place_id}) == 0:
        content = {
            "status": "failure",
            "message": "Invalid polling place id",
        }
        return content

    content = {
        "status": "success",
        "message": "Polling place id was successfully validated",
    }
    return content


async def validate_party_and_candidates(vote):
    candidates_ids = vote["candidates_ids"]

    if len(candidates_ids) > 5:
        content = {
            "status": "failure",
            "message": "Number of candidates is more than 5",
        }
        return content

    if len(set(candidates_ids)) != len(candidates_ids):
        content = {
            "status": "failure",
            "message": "Duplicate candidates ids",
        }
        return content

    parties = await get_parties_with_candidates()
    for party in parties:
        if party["_id"] == vote["party_id"]:
            candidate_match_count = 0
            for candidate in party["candidates"]:
                if candidate["_id"] in candidates_ids:
                    candidate_match_count += 1

            if candidate_match_count == len(candidates_ids):
                content = {
                    "status": "success",
                    "message": "Parties with candidates were successfully validated",
                }
                return content

            content = {
                "status": "failure",
                "message": "Invalid candidates ids",
            }
            return content

    content = {
        "status": "failure",
        "message": "Invalid party id",
    }
    return content


async def validate_tokens(tokens):
    if len(set(tokens)) != len(tokens):
        content = {
            "status": "failure",
            "message": "Duplicate tokens in the batch",
        }
        return content

    content = {
        "status": "success",
        "message": "Tokens were successfully validated",
    }
    return content


async def validate_token_with_polling_place_id(token, polling_place_id):
    DB = await get_database()

    if await DB.votes.count_documents({"token":token, "polling_place_id": polling_place_id}) != 0:
        content = {
            "status": "failure",
            "message": "Duplicate combination of token and polling place id",
        }
        return content
    content = {
        "status": "success",
        "message": "Token was successfully validated",
    }
    return content


async def validate_election_id(election_id):
    if election_id != config.ELECTION_ID:
        content = {
            "status": "failure",
            "message": "Invalid election id",
        }
        return content
    content = {
        "status": "success",
        "message": "Election id was successfully validated",
    }
    return content


async def validate_votes(request):
    DB = await get_database()

    polling_place_id = request.polling_place_id
    content = await validate_polling_place_id(polling_place_id)
    if content["status"] == "failure":
        return content

    key_pair = await DB.key_pairs.find_one({"polling_place_id": polling_place_id})

    if key_pair is None:
        content = {
            "status": "failure",
            "message": "Invalid private key for entered polling place id",
        }
        return content

    votes_to_be_inserted = []
    encrypted_votes = request.votes
    max_id = await get_max_id("votes")

    tokens_to_be_validated = []

    for _id, encrypted_vote in enumerate(encrypted_votes):
        private_key_pem = key_pair["private_key_pem"]

        # private_key_pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEAt9qwGYKhIjkGqQlUCbCbzbVf7H/pOsXyw49AYyy0fuvc04QP\nGZNZgB03cpmdPzylWsWskO9p1GPO8jQ8gf9FfVCFuqF+QRVwi8XRSrwyBsOo2GMp\nYwJaipVfr4bCbUMWs87kXGJmgu4o/+iXOD4kkupenVQF6H9T02kuPAhfotFIUZmL\nT68zee0TZ2JXk7WL9rn17ir9QL+S0NJz8C84Di8QfRVnT888Fv+2aCih2qmvdRHN\nedEXnHw0N5hVBWeoihFeV1LubKz+NM/2JhI4FDQ/skugwNK21iGPykFC+UvOhxW0\nEQ9GFbggEcGnYxKry4hV9g/4Z8aqktkngAnDNwIDAQABAoIBAEIfnndGUpKe5OTV\nrIphoN+OrIXACU9wkxu/gT5J/U6qoLzYAaBGrQlVOLR4SCROuP/ZGXP1D2BqVyso\nG1z7xO/Jjpctbt2UiupSRrA02F8zbp4IqAFqfsrZ51SXSIUIfHlF3z7Uyx6q7kb/\nzadWPkwyi73U0t0oMitWaGEB9/dz5luCr6Si13fnpxJP+ZhuuUjPJQAL2+iuUJcL\n/0GiN9mxISNXz6/a/umrUrpOZqsor13KjRBAAMyrOWNgsOmEhHXD+QIn24pxojuS\natIJOAW6lQDtn57LbV/Jg7ApxVsE2ICO+x5Bg9/RSxr4JOzzQ61zNq7JKMgcSdVx\nFcxSOGUCgYEAzQi9u9l5yv1j3drfJFTCwkmU6Snho56TPMAyzUu0tpn5/Ov9lpps\nnD95yltM83LpGbqIeSX9Qk1ZSE5wtLfvyAdh8JNYsHgFrJxAAy1zSyZUxHLE+nau\nUJJ+fnSq5Lwgq/DkQTj4den1tMOryADWHbUbhrFeYimSLZaM+S4aKoUCgYEA5Y4s\nXA3pCD/lwwDcXsntms+FSqPV1Sk456c1/zfeVGGx5hH4ebW4T0G0FoghJK5pC290\ne7TPc0UnpTyl66pBPaVuMcXx3xeWEcpiuvjhi+RQatkOYR88Mxh1zJfJK5+VZNAZ\nVGt2Bmbilb9BNC4juEqPJpoXHXch46nK6QneCYsCgYBj5zdz2ZKzquXHSwdhT3+a\nZXoOZl7Qd8rsVgYq7BGAy+P4LhDhGhuDwpYYWIZVNQ+Jfs9SoIUXklLHnZjjJaDL\nSXWaYGFdkw3IvlWedr3vxxyUoAuEsuFa1xaVjUlbrKMKxJSjhxvhcH9Nde40xNuP\nnBhud+wyTmkwl2PXYnRTdQKBgHIe9TSqgbBlO89vLR8+mg49ntFVk+fN/4lC2phP\n6QrgKrXrNzEiw0c7rdEJyhhXUMermCgr4no25hfCh+YaFScViCvccXtsWWHs0JqN\nQmvujIAh+oEUKzRns6CL0SoLwxSEVCNg7SMPoRO7KipLydxDzNjvABDY+hMZhVPH\nYQgzAoGABBg3hNE8chJWdpwvtm6MFqCrdaMVObUXM8N75yDGVq1IlJKqUkMG0nUb\n1+tDenWricdar7neK8AwQYHydWx7MTrBhl8JKCPHiXn5qYNAAIZmDcjLbtzpABAZ\n7MChVRyHUSVky0Cvb8Q7msrY0qjrddXoUy/NIjUymRqEHXNsF40=\n-----END RSA PRIVATE KEY-----"
        print(len(encrypted_vote))
        print(encrypted_vote)
        
        decrypted_vote = await electiersa.decrypt_vote(private_key_pem, encrypted_vote)
        decrypted_vote["polling_place_id"] = polling_place_id
        decrypted_vote["_id"] = max_id + 1 + _id

        content = await validate_party_and_candidates(decrypted_vote)
        if content["status"] == "failure":
            return content

        token = decrypted_vote["token"]
        content = await validate_token_with_polling_place_id(token, polling_place_id)
        if content["status"] == "failure":
            return content

        tokens_to_be_validated.append(token)

        election_id = decrypted_vote["election_id"]
        content = await validate_election_id(election_id)
        if content["status"] == "failure":
            return content

        votes_to_be_inserted.append(decrypted_vote)

    content = await validate_tokens(tokens_to_be_validated)
    if content["status"] == "failure":
        return content

    await DB.votes.insert_many(votes_to_be_inserted)

    content = {
        "status": "success",
        "message": "Vote was successfully precessed"
    }
    return content


@router.post("/vote", response_model=schemas.Message, status_code=status.HTTP_200_OK, responses={400: {"model": schemas.Message}})
async def vote(request: schemas.VotesEncrypted):
    """
    Process candidate's vote
    """

    content = await validate_votes(request)
    if content["status"] == "failure":
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)
    return content



@router.get("/voting-data", response_model=schemas.VotingData, status_code=status.HTTP_200_OK)
async def get_voting_data():
    parties_with_candidates = await get_parties_with_candidates()
    
    # -----
    # todo - toto musime potom vymazat, je to len pre ucel FASTAPI GUI
    parties_with_candidates = parties_with_candidates[:2]
    # -----
    
    # multilingual text for VT application
    texts = {
        "elections_name_short": {
            "sk": "Voľby do NRSR",
            "en": "Parliamentary elections",
        },
        "elections_name_long": {
            "sk": "Voľby do národnej rady Slovenskej republiky",
            "en": "Parliamentary elections of Slovak Republic",
        },
        "election_date": {
            "sk": "30.11.2021",
            "en": "30.11.2021",
        }
    }
    
    image_paths = glob.glob("data/nrsr_2020/logos/*")
    for image_path in image_paths:
        for party_with_candidates in parties_with_candidates:
            image = image_path.split("/")[-1]
            if image == party_with_candidates["image"]:
                with open(image_path, "rb") as file:
                    image_bytes = base64.b64encode(file.read())
                    party_with_candidates["image_bytes"] = image_bytes

    content = {
        "parties": parties_with_candidates,
        "texts": texts
    }
    return content
