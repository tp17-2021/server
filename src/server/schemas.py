from typing import Collection
from pydantic import BaseModel
from typing import List

class Collection(BaseModel):
    name: str
    keys: List[str] = []

class ResponseDBSchema(BaseModel):
    status: str
    message: str
    collections: List[Collection] = []



class Vote(BaseModel):
    token: str
    candidate_id: str
    party_id: str
    office_id: str
    election_id: str


class ServerCandidate(BaseModel):
    candidate_id: str


server_vote_example = None
class ServerVote(BaseModel):
    token: str
    candidates: List[ServerCandidate] = []
    party_id: str
    election_id: str
    office_id: str

    class Config:
        global server_vote_example
        server_vote_example = {
            "example": {
                "token": "token",
                "candidates": [
                    {
                        "candidate_id" : "some_id"
                    },
                    {
                        "candidate_id" : "another_id"
                    }     
                ],
                "party_id": "custom_id1",
                "office_id": "custom_id2",
                "election_id": "custom_id3",
            }
        }
    
class RequestVoteSchema(BaseModel):
    data: List[ServerVote] = []
    office_id: str

    class Config:
        global server_vote_example
        request_vote_example = { 
            "data": [
                server_vote_example
            ],
            "office_id": "custom_id4"
        }

class ResponseVoteSchema(BaseModel):
    status: str
    message: str
    vote: Vote

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
    _id: str    #todo: transform from str to ObjectId
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