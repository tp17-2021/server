from typing import Collection
from pydantic import BaseModel, validator, Extra, Field
from typing import List


class Message(BaseModel):
    message: str


class Collection(BaseModel):
    name: str
    keys: List[str] = []


class ResponseDatabaseSchema(BaseModel):
    status: str
    message: str
    collections: List[Collection] = []

# class Vote(BaseModel):
#     token: str
#     candidate_id: str
#     party_id: str
#     office_id: str
#     election_id: str


# TODO pridat Object id fields potom
class ServerPollingPlace(BaseModel):
    region_code: int
    region_name: str
    administrative_area_code: int
    administrative_area_name: str
    county_code: int
    county_name: str
    municipality_code: int
    municipality_name: str
    polling_place_number: int
    registered_voters_count: int

    class Config:
        schema_extra = {
            "region_code": 1,
            "region_name": "Bratislavský kraj",
            "administrative_area_code": 101,
            "administrative_area_name": "Bratislava",
            "county_code": 101,
            "county_name": "Bratislava I",
            "municipality_code": 528595,
            "municipality_name": "Bratislava - Staré Mesto",
            "polling_place_number": 5,
            "registered_voters_count": 1362
        }

class ServerCandidate(BaseModel):
    candidate_id: str

# server_vote_example = None


class ServerVote(BaseModel):
    token: str
    candidates: List[ServerCandidate] = []
    party_id: str
    election_id: str
    office_id: str

    class Config:
        schema_extra = {
            "example": {
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
        }


class RequestServerVoteSchema(BaseModel):
    votes: List[ServerVote] = Field(...)
    office_id: str = Field(...)

    @validator('votes')
    def name_must_contain_space(cls, votes):
        if not len(votes):
            raise ValueError('cannot be empty')
        return votes

    class Config:
        extra = Extra.forbid
        schema_extra = {
            "example": {
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
                "office_id": "office_id1"
            }
        }


class ResponseServerVoteSchema(BaseModel):
    status: str
    message: str
    votes: List[ServerVote] = []
    office_id: str

# kandidat
# strana
# vote


# pre databazu

# DatabaseCandidate(BaseModel)
    # sample_candidate = {
    #     "_id": random.randint(10**6, 10**7), ObjectId (str)
    #     "order" : random.randint(10, 10000), int
    #     "first_name" : "Jozef",
    #     "last_name" : "Králik",
    #     "middle_names" : "Jožko",
    #     "degrees_before" : "Ing. Mgr.", List[str] = []
    #     "degrees_after" : "PhD.", str
    #     "personal_number" : "EL180968", str
    #     "occupation": "Calisthenics enthusiast, crypto trader, physicist, daš si hrozienko?", str/trxt
    #     "age" : random.randint(18, 110), int
    #     "residence": "Prievidza", str
    #     "party_id" : "1" str/int
    # }

# Party
# candidates: List[Cand]

# ResponseDatabaseData(BaseModel)
# parties = List[Party]


class DatabaseParty(BaseModel):
    _id: str  # todo: transform from str to ObjectId
    name: str
    abbreviation: str
    image: str

    class Config:
        schema_extra = {
            "example": {
                "_id": "19",
                "name": "SMER - sociálna demokracia",
                "abbreviation": "SMER - SD",
                "image": "don_roberto_logo.jpg"
            }
        }


# Elections
# poskytnut configurak
# zavolit podla schemy dany hlas (netreba overat) + vlozit do DB


# Statistics
# jednoduche vyhodnotenie
# porataj pogroupovane podla can Id a party id
# pomenovanie na predbezne (urcene len pre G a pre Admina + TV) / vysledky ()


# schemas naming convention

# Resquest or Response
# <Request/Response><Elections/Statistics/Database/Server/...><What Optional><Schema>

# Nested class
# <Elections/Statistics/Database/Server/...><What>
