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

class RequestVoteSchema(Vote):
    pass

class ResponseVoteSchema(BaseModel):
    status: str
    message: str
    vote: Vote
