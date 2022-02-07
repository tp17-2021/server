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

class Text(BaseModel):
    sk: str
    en: str

class Texts(BaseModel):
    elections_name_short: Text
    elections_name_long: Text
    election_date: Text

class Candidate(BaseModel):
    _id: int
    party_number: int
    order: int
    first_name: str
    last_name: str
    degrees_before: str
    age: int
    occupation: str
    residence: str
    
class Party(BaseModel):
    _id: int
    party_number: int
    name: str
    abbreviation: str
    image: str
    image_bytes: str
    candidates: List[Candidate] = []

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

class VotingData(BaseModel):
    parties: List[Party] = []
    texts: Texts

class KeyPair(BaseModel):
    polling_place_id: str
    private_key_pem: str
    public_key_pem: str

class KeyPairs(BaseModel):
    key_pairs: List[KeyPair] = []

class Vote(BaseModel):
    token: str
    party_id: int
    election_id: str
    candidates_ids: List[int] = []

class VoteEncrypted(BaseModel):
    encrypted_vote: str
    tag: str
    nonce: str
    encrypted_aes_key: str

class VotesEncrypted(BaseModel):
    polling_place_id: int
    votes: List[VoteEncrypted] = []

    class Config:
        schema_extra = {
            "example": {
                "polling_place_id": 0,
                "votes": [
                    {
                        "encrypted_vote": "cZSkFnlwH/VZ30WmvmbrF7GjMqWKp8zxDYNHMwR97cVqLM6FXOx6uz21/CuDvvNvSE+IULmQxp8fNNpu/zaewzMLCvXP/Vam9rVCU4FCjiiYVZZrMiyLVa5+/zPqBCaIwMqBks3O2S0OSrk=",
                        "tag": "CZAvk1wCIbWZhcD7ZdSFOw==",
                        "nonce": "g7zmCLbn8bluYUq1nrW10g==",
                        "encrypted_aes_key": "Q0LlxTxdbRMzllV03TX0GW1gSxs6WsDzoNx/DufPFWyyyVVnNj/A9Gp0Ujo9aKX5ywvZTXomP4zEgL1l7QfYEk0pHrjWj8L4HxTWNcfS6jRxFuRkAzhCVo0Dpr8cntDZlUjL7vOIvdIbA+3xGh4NeLcwmbFs3RoIDCh4wppklkgpPxs7cubYzoOUd9pcfiwHD+t3bjgVDnWVweTORZHB/wnS/TTPsH+ZpPsAGKBEjL3Mae/ITEOfCN0auxvNw01pbYVohMAB/Wb4JeN8Utd6O6DUPUBpcPPRS1Hk5gtYTy3su4uSYOqpcDdw+sTYfTPB259D0eAVoJ25zBhlpfzP5Q=="
                    }
                ]
            }
        }

class VoteToBeEncrypted(BaseModel):
    public_key_pem: str
    aes_key: str
    vote: Vote

    class Config:
        schema_extra = {
            "example": {
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs6lvNfr+Eo6Mt+mW95fh\njUbCRygCNok8Y8yIu502lpDiz3bNdR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7I\nEpRSmY1nElabMoBbU2vsPWBsu7WR31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPu\nRVtuHy/q2tD5sY2ekWJc1YsoeQ5JDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c\n2P4NpNgSJ2NT8aF/bDbu3sQk9QuQXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchq\nrYj5Xnql/wcrnyOhcgeKsOBieH/fETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG4\n7QIDAQAB\n-----END PUBLIC KEY-----",
                "aes_key": "K6COJ/CWsJxA2RqvHoaF1RDxbfnZGa9+1PY8ppVD6EA=",
                "vote": {
                    "token": "fjosjfidsw",
                    "party_id": 10,
                    "election_id": "election_id",
                    "candidates_ids": [
                        1158,
                        1077,
                        1191,
                    ]
                }
            }
        }


class VoteToBeDecrypted(BaseModel):
    encrypted_vote: str
    tag: str
    nonce: str
    encrypted_aes_key: str
    private_key_pem: str

    class Config:
        schema_extra = {
            "example": {
                "encrypted_vote": "cZSkFnlwH/VZ30WmvmbrF7GjMqWKp8zxDYNHMwR97cVqLM6FXOx6uz21/CuDvvNvSE+IULmQxp8fNNpu/zaewzMLCvXP/Vam9rVCU4FCjiiYVZZrMiyLVa5+/zPqBCaIwMqBks3O2S0OSrk=",
                "tag": "CZAvk1wCIbWZhcD7ZdSFOw==",
                "nonce": "g7zmCLbn8bluYUq1nrW10g==",
                "encrypted_aes_key": "Q0LlxTxdbRMzllV03TX0GW1gSxs6WsDzoNx/DufPFWyyyVVnNj/A9Gp0Ujo9aKX5ywvZTXomP4zEgL1l7QfYEk0pHrjWj8L4HxTWNcfS6jRxFuRkAzhCVo0Dpr8cntDZlUjL7vOIvdIbA+3xGh4NeLcwmbFs3RoIDCh4wppklkgpPxs7cubYzoOUd9pcfiwHD+t3bjgVDnWVweTORZHB/wnS/TTPsH+ZpPsAGKBEjL3Mae/ITEOfCN0auxvNw01pbYVohMAB/Wb4JeN8Utd6O6DUPUBpcPPRS1Hk5gtYTy3su4uSYOqpcDdw+sTYfTPB259D0eAVoJ25zBhlpfzP5Q==",
                "private_key_pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAs6lvNfr+Eo6Mt+mW95fhjUbCRygCNok8Y8yIu502lpDiz3bN\ndR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7IEpRSmY1nElabMoBbU2vsPWBsu7WR\n31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPuRVtuHy/q2tD5sY2ekWJc1YsoeQ5J\nDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c2P4NpNgSJ2NT8aF/bDbu3sQk9QuQ\nXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchqrYj5Xnql/wcrnyOhcgeKsOBieH/f\nETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG47QIDAQABAoIBAAEotU5QfGpm8gUF\n/64cOMs1Bm/4E+QmCFrF5IQ1VFvlBBmQGZGko6i6AHR0CtCN2OuVAne9sTtfYyjU\nLvPdzUcMQ3q40+B3n5BB6UvFZ2SIiu1RE3nDCRyFx/VWATEqwZKTmaEUsO1BMHwx\nJWW5+K4tb1HunUZ20M2OEfkps39438Vk1R4I/kJqhp8E7mLYshBHyK1OwOgiInE4\n1Z2SwAhvGKnNE3TnBlV7/K5XFQg3b7QWORHvlvnNHU7ed8TXmizp7No6Qxl1ZJ2z\nier3f+XiMAryIb7AyBJyIWGnQllrDhff5hhNObltLmmaAkQm3LSsJ52GU9e4i/6c\nF/sshLECgYEAu78IM4Sj3D+wd6lMNVInU7Np8o8L5Ihq9Y1ccHmyvbVdxeGPIfKo\n/j/WwoCQJPKFQJLjQru3s1nVOOYNE5/CUQEEeFguzRL43UtzywONc1+L4a2MOnqO\n8ywQF1OrxByFy9eFLdN5ETdDhriajx8VM0hRrmeLsiGcmVZet1lFjjkCgYEA9PoD\n3x2qaCrTe3mZPHzfayHYWVFFxvRYOjxmIbOdzQZPeQA1tXEHyHnY/z3ibA+v3iQu\nQ2n5RQM4/+ItjS2xrwL+hlU3yue67HfBuUyFcFjhEUu0sdN4439d3K9hAeX7eTfB\nZ2CsNieqPxYZj6tSL4+0Fru4o4VpD79u7pSlgFUCgYAdWiJoG4aauoJWUuuNMojf\ndx9LQr3zPriqJy2akAw3yJEejMMZ5ZwyE7z5r6vZeukGTXCmUD7KFXNWb/D/bmys\nyWHvhqnaeerafh9eT/HfZcKyx7Uyt1J+BheF7hjeki8AzXMO1Q8Kd/9gop/XXF6u\nI9JRV/LpKIQZHP214IkVUQKBgQCpqO09fIIkGmTUwuZJagIhZBM96Hd2zoq76lCh\nTpAfChvIJUkNG/bT9O8/9k/1nveh1VTlA2PLU+wJ606408iW+G/mAObe85YVZusX\ntdNEd4mIPPIrpdW3WOJckGmSswBydxbOzbj22Imjn16cjX4hylhi1ieNuDuG2IGv\nYess8QKBgQCrT1ATnUxqacw/x8RRJpZWV4rnrkujA2XPLu4YaMODzVSkk+HVEabH\nJtA4AV6O0bneAgywBltg9wL0L98Q6ckuEo6hA9rskvwxQAk9uawJDzy1Bq/aEcSD\nu707LpYyMboRA/+1Sw8GEYF1iKdVJnGN1pjse4V4mJvobPPEZ+4Atw==\n-----END RSA PRIVATE KEY-----"
            }
        }


class VoteDecrypted(BaseModel):
    vote: Vote


# Statistics
# jednoduche vyhodnotenie
# porataj pogroupovane podla can Id a party id
# pomenovanie na predbezne (urcene len pre G a pre Admina + TV) / vysledky ()
