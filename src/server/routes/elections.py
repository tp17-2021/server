# General modules
import os
import base64
import glob

# FastAPI modules
from fastapi import status, APIRouter, HTTPException
from fastapi.responses import JSONResponse

# Server modules
from src.server import config
from src.server import schemas
from src.server.database import DB, get_database
from src.server.database import get_parties_with_candidates, get_max_id

# Custom module from PyPI
from electiersa import electiersa

# TODO pomenovat
from elasticsearch import Elasticsearch

# Main elastic search connection
ES = Elasticsearch(
    hosts=[{
        "scheme": "http",
        "host": os.environ["ELASTIC_HOST"],
        "port": int(os.environ["ELASTIC_PORT"])
    }])

# Create FastAPI router
router = APIRouter(
    prefix="/elections",
    tags=["Elections"],
)


async def validate_polling_place_id(polling_place_id: int) -> dict:
    """ Validate polling place id """

    DB = await get_database()

    if await DB.key_pairs.count_documents({"polling_place_id": polling_place_id}) == 0:
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


async def validate_party_and_candidates(vote: dict) -> dict:
    """ Validate party and candidates based on provided vote """

    candidate_ids = vote["candidate_ids"]

    if len(candidate_ids) > 5:
        content = {
            "status": "failure",
            "message": "Number of candidates is more than 5",
        }
        return content

    if len(set(candidate_ids)) != len(candidate_ids):
        content = {
            "status": "failure",
            "message": "Duplicate candidates ids",
        }
        return content

    if vote["party_id"] is None:

        if len(candidate_ids) != 0:
            content = {
                "status": "failure",
                "message": "When party_id is None there is no possibility to have length of candidate_ids greater than zero",
            }
        else:
            content = {
                "status": "success",
                "message": "Parties with candidates were successfully validated",
            }
        return content

    parties = await get_parties_with_candidates()
    for party in parties:
        if party["_id"] == vote["party_id"]:
            candidate_match_count = 0
            for candidate in candidate_ids:
                if candidate in [i["_id"] for i in party["candidates"]]:
                    candidate_match_count += 1

                else:
                    err_msg = f'candidate |{candidate}| is not in party |{party["_id"]}|'

                    content = {
                        "status": "failure",
                        "message": "Invalid candidates ids - " + err_msg,
                    }
                    return content

            content = {
                "status": "success",
                "message": "Parties with candidates were successfully validated",
            }
            return content

    content = {
        "status": "failure",
        "message": "Invalid party id",
    }
    return content


async def validate_tokens(tokens: list) -> dict:
    """ Validate tokens """

    content = {
        "status": "success",
        "message": "Tokens were successfully validated",
    }

    if "ACCEPT_TOKEN_VALID" in os.environ and os.environ["ACCEPT_TOKEN_VALID"] == "1":
        return content

    if len(set(tokens)) != len(tokens):
        content = {
            "status": "failure",
            "message": "Duplicate tokens in the batch",
        }
    return content


async def validate_token_with_polling_place_id(token: str, polling_place_id: int) -> dict:
    """ Validate token with polling place id """

    DB = await get_database()

    content = {
        "status": "success",
        "message": "Token was successfully validated",
    }

    if 'ACCEPT_TOKEN_VALID' in os.environ and os.environ['ACCEPT_TOKEN_VALID'] == '1' and token == "valid":
        return content

    if await DB.votes.count_documents({"token": token, "polling_place_id": polling_place_id}) != 0:
        content = {
            "status": "failure",
            "message": "Duplicate combination of token and polling place id",
        }
    return content


async def validate_election_id(election_id: str) -> dict:
    """ Validate election id """

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


async def validate_decryption(decrypted_vote: dict, polling_place_id: int, max_id: int, _id: int) -> dict:
    """ Validate decryption """

    if decrypted_vote is None:
        content = {
            "status": "failure",
            "message": "Invalid decryption - decrypted vote is none",
        }
        return content
    try:
        decrypted_vote["polling_place_id"] = polling_place_id
        # decrypted_vote["_id"] = max_id + 1 + _id
    except Exception as e:
        content = {
            "status": "failure",
            "message": "Invalid decryption - unspecified",
        }
        return content

    content = {
        "status": "success",
        "message": "Decryption was successfully validated",
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
    votes = request.votes
    # max_id = await get_max_id("votes")

    tokens_to_be_validated = []

    for _id, encrypted_vote in enumerate(votes):
        private_key_pem = key_pair["private_key_pem"]
        g_public_key_pem = key_pair["g_public_key_pem"]

        decrypted_vote = electiersa.decrypt_vote(
            encrypted_vote, private_key_pem, g_public_key_pem)
        content = await validate_decryption(decrypted_vote, polling_place_id, 0, _id)
        if content["status"] == "failure":
            return content

        decrypted_vote["polling_place_id"] = polling_place_id
        # decrypted_vote["_id"] = max_id + 1 + _id

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


@router.post("/vote", response_model=schemas.Message, responses={400: {"model": schemas.Message}})
async def vote(request: schemas.VotesEncrypted) -> dict:
    """
    Process candidate's vote
    """

    content = await validate_votes(request)
    if content["status"] == "failure":
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)
    return content


async def get_config_file(mode="all", polling_place_id=None):
    DB = await get_database()

    polling_place = None
    polling_places = None

    if mode == "gateway" and polling_place_id is not None:
        polling_place = await DB.polling_places.find_one({"_id": polling_place_id}, {"_id": 0})

    if mode == "all":
        polling_places = [polling_place async for polling_place in DB.polling_places.find()]

    print(polling_place, polling_places, flush=True)
    parties_with_candidates = await get_parties_with_candidates()
    key_pairs = [key_pair async for key_pair in DB.key_pairs.find()]

    regions = [polling_place async for polling_place in DB.polling_places.aggregate([
        {
            '$group': {
                '_id': '$region_code',
                'name': {
                    '$first': '$region_name'
                }
            }
        },
        {
            '$sort': {
                '_id': 1
            }
        },
        {
            '$project': {
                'code': '$_id',
                'name': '$name',
                '_id': 0
            }
        }
    ])]

    counties = [polling_place async for polling_place in DB.polling_places.aggregate([
        {
            '$group': {
                '_id': '$county_code',
                'name': {
                    '$first': '$county_name'
                },
                'region_code': {
                    '$first': '$region_code'
                }
            }
        },
        {
            '$sort': {
                '_id': 1
            }
        },
        {
            '$project': {
                'code': '$_id',
                'name': '$name',
                'region_code' : '$region_code',
                '_id': 0
            }
        }
    ])]

    municipalitites = [polling_place async for polling_place in DB.polling_places.aggregate([
        {
            '$group': {
                '_id': '$municipality_code',
                'name': {
                    '$first': '$municipality_name'
                },
                'region_code': {
                    '$first': '$region_code'
                },
                'county_code': {
                    '$first': '$county_code'
                }
            }
        },
        {
            '$sort': {
                'name': 1
            }
        }, {
            '$project': {
                'code': '$_id',
                'name': '$name',
                'region_code' : '$region_code',
                'county_code' : '$county_code',
                '_id': 0
            }
        }
    ])]

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
        },
        "contact": {
            "title": {
                "sk": "Volebná centrála Bratislava",
                "en": "Volebná centrála Bratislava"
            },
            "contact_person": "Jožko Mrkvička",
            "address": "Volebná 1, 853 01 Bratislava",
            "phone": "+421 910 123 456",
            "email": "support@volby.sk"
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

    if mode == 'gateway':
        return {
            "polling_place": polling_place,
            "parties": parties_with_candidates,
            "key_pairs": key_pairs,
            "texts": texts
        }
    else:
        return {
            "parties": parties_with_candidates,
            "key_pairs": key_pairs,
            "texts": texts,
            "regions": regions,
            "counties": counties,
            "municipalities": municipalitites
        }

# TODO pridat tam schemu, neviem preco je to takto bez toho, ale treba to vratit naspat, asi sa nieco menilo...
# @router.get("/voting-data", response_model=schemas.VotingData, status_code=status.HTTP_200_OK)
@router.get("/voting-data")
async def get_voting_data() -> dict:
    """
    Download voting data json (used on statistics FE) using
    command curl http://localhost:8222/elections/voting-data > config.json
    """

    content = await get_config_file()
    return content


@router.get("/gateway-config", status_code=status.HTTP_200_OK)
async def get_gateway_config(polling_place_id: int) -> dict:
    """
    Download gateway config data json using command
    curl http://localhost:8222/elections/gateway-config > config.json
    """

    content = await get_config_file(
        mode="gateway", polling_place_id=polling_place_id)

    if(content['polling_place'] == None):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Polling place not found"
        )
    return content
