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
    _id: int
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

class KeyPair(BaseModel):
    _id: int
    polling_place_id: int
    aes_key: str
    private_key_pem: str
    public_key_pem: str

class VotingData(BaseModel):
    polling_places: List[PollingPlace] = []
    parties: List[Party] = []
    key_pairs: List[KeyPair] = []
    texts: Texts

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
                        "encrypted_vote": "TLrV9+z9R/0fviMkhOjRrtW3ks6pnRY8/quf23hG3AAth+2EnWyX1ED/kIW+UlXbj94aTj6zvjCtuegFANaUxOyuvwQMVdZ8M8czMKU74Wsc9cVfw9xIBYwJZi2Ypg2gnEIWl1L/+iil9jA=",
                        "tag": "exSFa3vi15tCqpmq9V/9Gg==",
                        "nonce": "mVjjrf5NmH4Bs0VlH20ltA==",
                        "encrypted_aes_key": "ZLkQJmDyZRNxsqAnqIOyVaBaA1Tu0NFw2PaKAy4c/eigkA8LBLVQqem69jkTjM9KZIsAzbDyh41KNwYaawXxRrAebm+v2iQg1aZUdsAxfzEWVp5k3+b1MuRcD393o5FkmML+7zxe0lt/fCmjr2Q6OYeilJI+IbVqii8SxABW6fH2uafPTRGJGSS//ne70oiIBDXM1m6ytEThKPW2rgb7ZqGxKBJyiev+fyCyNqrip4fZTnpHEwqkVBWTeRbzBtAMjFWOv234wSBvbM9dLk6D9P9nZCVD6hE3JQk842bUPI7OkyR5Y2DO7qVo42i1ijdK/HCNigoh76Y20SETS84E3g=="
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
                "aes_key": "LSH63IWHrJmm7VkLt+eTX35ON5jYqtYBf3hDeC4ZYkU=",
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
                "encrypted_vote": "jbKrPSBcBVi84BL5pqROwyqFi/9dotIJ7x/13WevatP6Ydwd6nKWdCYy9M+zv/BJG6yQu2MVn4q56je/rRiVZqoA7pD5E98pJ3UeazelmaIzsuTqR4ffhvLBHvRhdhOEygjmNO8Vgezgx5Y=",
                "tag": "VzRG72yFU96eZoUTOy0Nsw==",
                "nonce": "R3b4b8vfjA1hv/bhvhBWLw==",
                "encrypted_aes_key": "p/C8qtxDztAmYP/h7nAAGap2ODijGOkGXG3m9kboc5tUXGusyzlRJJmNLS70NosX7xx9dhY1ftOKQ9NTj+NYikNYBYzeC/F9HSqo21/qWmIYjfrx13pnVaoLa7ezjre96MwbcqdKnmrxCb0rsH5TgEDq2vwpDif0tP+7Iec8A3dikC5x54fehbqaK1nnQDTbvsHBJQjpVfKhI5Oy0zq0IwV0XR080cWeGF17qevBdz8K4ybFie5qa5iy6IXTZ1E1Vy6ibpmXG+032vuyAPUyY5zQCRkqNc523ayQo0MG2PHDmKHmhFLqpgyBVl0CS3j8cwjKCIGhFNBCV2WMyrPzRg==",
                "private_key_pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAs6lvNfr+Eo6Mt+mW95fhjUbCRygCNok8Y8yIu502lpDiz3bN\ndR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7IEpRSmY1nElabMoBbU2vsPWBsu7WR\n31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPuRVtuHy/q2tD5sY2ekWJc1YsoeQ5J\nDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c2P4NpNgSJ2NT8aF/bDbu3sQk9QuQ\nXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchqrYj5Xnql/wcrnyOhcgeKsOBieH/f\nETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG47QIDAQABAoIBAAEotU5QfGpm8gUF\n/64cOMs1Bm/4E+QmCFrF5IQ1VFvlBBmQGZGko6i6AHR0CtCN2OuVAne9sTtfYyjU\nLvPdzUcMQ3q40+B3n5BB6UvFZ2SIiu1RE3nDCRyFx/VWATEqwZKTmaEUsO1BMHwx\nJWW5+K4tb1HunUZ20M2OEfkps39438Vk1R4I/kJqhp8E7mLYshBHyK1OwOgiInE4\n1Z2SwAhvGKnNE3TnBlV7/K5XFQg3b7QWORHvlvnNHU7ed8TXmizp7No6Qxl1ZJ2z\nier3f+XiMAryIb7AyBJyIWGnQllrDhff5hhNObltLmmaAkQm3LSsJ52GU9e4i/6c\nF/sshLECgYEAu78IM4Sj3D+wd6lMNVInU7Np8o8L5Ihq9Y1ccHmyvbVdxeGPIfKo\n/j/WwoCQJPKFQJLjQru3s1nVOOYNE5/CUQEEeFguzRL43UtzywONc1+L4a2MOnqO\n8ywQF1OrxByFy9eFLdN5ETdDhriajx8VM0hRrmeLsiGcmVZet1lFjjkCgYEA9PoD\n3x2qaCrTe3mZPHzfayHYWVFFxvRYOjxmIbOdzQZPeQA1tXEHyHnY/z3ibA+v3iQu\nQ2n5RQM4/+ItjS2xrwL+hlU3yue67HfBuUyFcFjhEUu0sdN4439d3K9hAeX7eTfB\nZ2CsNieqPxYZj6tSL4+0Fru4o4VpD79u7pSlgFUCgYAdWiJoG4aauoJWUuuNMojf\ndx9LQr3zPriqJy2akAw3yJEejMMZ5ZwyE7z5r6vZeukGTXCmUD7KFXNWb/D/bmys\nyWHvhqnaeerafh9eT/HfZcKyx7Uyt1J+BheF7hjeki8AzXMO1Q8Kd/9gop/XXF6u\nI9JRV/LpKIQZHP214IkVUQKBgQCpqO09fIIkGmTUwuZJagIhZBM96Hd2zoq76lCh\nTpAfChvIJUkNG/bT9O8/9k/1nveh1VTlA2PLU+wJ606408iW+G/mAObe85YVZusX\ntdNEd4mIPPIrpdW3WOJckGmSswBydxbOzbj22Imjn16cjX4hylhi1ieNuDuG2IGv\nYess8QKBgQCrT1ATnUxqacw/x8RRJpZWV4rnrkujA2XPLu4YaMODzVSkk+HVEabH\nJtA4AV6O0bneAgywBltg9wL0L98Q6ckuEo6hA9rskvwxQAk9uawJDzy1Bq/aEcSD\nu707LpYyMboRA/+1Sw8GEYF1iKdVJnGN1pjse4V4mJvobPPEZ+4Atw==\n-----END RSA PRIVATE KEY-----"
            }
        }



class VoteDecrypted(BaseModel):
    vote: Vote


# Statistics
# jednoduche vyhodnotenie
# porataj pogroupovane podla can Id a party id
# pomenovanie na predbezne (urcene len pre G a pre Admina + TV) / vysledky ()
