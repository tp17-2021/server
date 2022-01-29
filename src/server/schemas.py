from typing import Collection
from pydantic import BaseModel, validator, Extra, Field
from typing import List


class Message(BaseModel):
    status: str
    message: str

class Collection(BaseModel):
    name: str
    keys: List[str] = []

class Collections(BaseModel):
    collections: List[Collection] = []

# TODO pridat Object id fields potom
# naozaj to treba?
class PollingPlace(BaseModel):
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
            "example": {
                "region_code": 1,
                "region_name": "Bratislavský kraj",
                "administrative_area_code": 101,
                "administrative_area_name": "Bratislava",
                "county_code": 101,
                "county_name": "Bratislava I",
                "municipality_code": 528595,
                "municipality_name": "Bratislava - Staré Mesto",
                "polling_place_number": 1,
                "registered_voters_count": 1234
            }
        }

class Data(BaseModel):
    token: str
    party_id: str
    election_id: str
    candidates_ids: List[str] = []

class Vote(BaseModel):
    polling_place_id: str
    data: Data

    class Config:
        schema_extra = {
            "example": {
                "polling_place_id": "61f42c5e0bca18684cc2fe4e",
                "data": {
                    "token": "ABCDEFGHIJ",
                    "party_id": "61f42c5b0bca18684cc2f385",
                    "election_id": "todo",
                    "candidates_ids": [
                        "61f42c5b0bca18684cc2f39e",
                        "61f42c5b0bca18684cc2f39f",
                        "61f42c5b0bca18684cc2f3a0",
                        "61f42c5b0bca18684cc2f3a1",
                        "61f42c5b0bca18684cc2f3a2"
                    ]
                }
            }
        }


class Votes(BaseModel):
    votes: List[Vote] = []

    # @validator('votes')
    # def name_must_contain_space(cls, votes):
    #     if not len(votes):
    #         raise ValueError('cannot be empty')
    #     return votes

    class Config:
        # extra = Extra.forbid

        schema_extra = {
            "example": {
                "votes": [
                    {
                        "polling_place_id": "61f42c5e0bca18684cc2fe4e",
                        "data": {
                            "token": "ABCDEFGHIJ",
                            "party_id": "61f42c5b0bca18684cc2f385",
                            "election_id": "todo",
                            "candidates_ids": [
                                "61f42c5b0bca18684cc2f39e",
                                "61f42c5b0bca18684cc2f39f",
                                "61f42c5b0bca18684cc2f3a0",
                                "61f42c5b0bca18684cc2f3a1",
                                "61f42c5b0bca18684cc2f3a2"
                            ]
                        }
                    },
                    {
                        "polling_place_id": "polling_place_id2",
                        "data": {
                            "token": "token2",
                            "party_id": "61f3da839f441c468647f4cb",
                            "election_id": "election_id1",
                            "candidates_ids": [
                                "candidate_id1",
                                "candidate_id2",
                                "candidate_id3",
                            ]
                        }
                    }
                ]
            }
        }


class Text(BaseModel):
    sk: str
    en: str

class Texts(BaseModel):
    elections_name_short: Text
    elections_name_long: Text
    election_date: Text

class Candidate(BaseModel):
    _id: str
    party_number: str
    order: int
    first_name: str
    last_name: str
    degrees_before: str
    age: int
    occupation: str
    residence: str
    
class Party(BaseModel):
    _id: str
    party_number: int
    name: str
    abbreviation: str
    image: str
    image_bytes: str
    candidates: List[Candidate] = []

class VotingData(BaseModel):
    parties: List[Party] = []
    texts: Texts

class KeyPair(BaseModel):
    polling_place_id: str
    private_key_pem: str
    public_key_pem: str

class KeyPairs(BaseModel):
    key_pairs: List[KeyPair] = []

class RequestEncryptionDecryptionTestSchema(BaseModel):
    message: str

    class Config:
        # extra = "allow"
        schema_extra = {
            "example": {
                "message": "Hi there!",
            }
        }

class VoteEncrypted(BaseModel):
    polling_place_id: str
    data: str

class VotesEncrypted(BaseModel):
    votes: List[VoteEncrypted] = []

class VoteToBeEncrypted(BaseModel):
    public_key_pem: str
    polling_place_id: str
    data: Data

    class Config:
        schema_extra = {
            "example": {
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA33n5V5YVqcrlfA1hKc+U\nrqOApWNrCRv3qqf1t+HK1wp1G7ljNmeeaeCGTC+utCLcPT0IwPXHi9itnvhlhh0B\n4M2DJlKoxGtLu+ujPS7YTPaky95rJFprhFmGwptCs4rbYfgkHaLBHOVFDB3UXkFL\nnzauqi+g44aOZtzRtwJtMp6PTe1pP5jNfhVNCz21+qZmDNvHRQtkCH+Z+75cWE//\nWVmbi6HK2UMcfJ0nPCYG0ngTh6io5LHmQCa2iYDLF8RRcklhQkRhKwHhbxCI0QVv\nrlZ4jNGi9Ml1zoo0nwkk9s93iGX26wpejv7g+8hnqQpQj5ACG9z+6mq7Vm5VuEDP\nQZ91ECLoo3Q9zorffAECdVKvW+D4p4F2jkclFeXP6dF0onTkN3tiJTinPCxol8ij\n9RgfKYYFuON7OJravA+xStLz45novy7A0n5dqzd4cTay+nF6fpR9/KvE4Tg6RSew\nrgjF1YIgmpgFjhOMvWJ8SnBahkURUTmb4CEgTpyOiRvq28OYxzBctUfCh8//jH95\ndL91AFhWDPtzwpKiIkaNGDwkVz2r123MeKg/MBWGtWdl6I+6mI3qeEAZNgfl5Wzd\nNkR8lqZZ/GcNVHYXbWTGAjw37i2+/V2Twqta7R6l/GEcM4XDhMci6eYtYABj/iJP\n8D4lStZZSaQMzWoeXGuZkakCAwEAAQ==\n-----END PUBLIC KEY-----",
                "polling_place_id": "61f42c5e0bca18684cc2fe4e",
                "data": {
                    "token": "ABCDEFGHIJ",
                    "party_id": "61f42c5b0bca18684cc2f385",
                    "election_id": "todo",
                    "candidates_ids": [
                        "61f42c5b0bca18684cc2f39e",
                        "61f42c5b0bca18684cc2f39f",
                        "61f42c5b0bca18684cc2f3a0",
                        "61f42c5b0bca18684cc2f3a1",
                        "61f42c5b0bca18684cc2f3a2"
                    ]
                }
            }
        }

class VoteDecrypted(BaseModel):
    polling_place_id: str
    data: Data


# Statistics
# jednoduche vyhodnotenie
# porataj pogroupovane podla can Id a party id
# pomenovanie na predbezne (urcene len pre G a pre Admina + TV) / vysledky ()
