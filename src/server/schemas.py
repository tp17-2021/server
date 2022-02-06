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

class VotesEncrypted(BaseModel):
    polling_place_id: int
    votes: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "polling_place_id": 0,
                "votes": [
                    "PBIUvoS/yo4gAnK8k+jvKmVVKPglzwIMEYxGBwVZv1iQvrtQIpiTd5fq4Ry+vG+uiiZXav8ODZU1Y7AG88mirNco4Mjt+qqDfQ9S4lQxAe4aJdOI+MIYQpg0AyzfCgQmfQMpQRnrHl9Bd7FOMUh3jCCrEwsi7xYSKGmssRpgYfFNlP7g3kxmiDcFOClu/7ZZ44nZD+WsDtNNcsSqTUJCTeZ7YlZGBX4bi98qDJufqhWFM9OklkKavMklxyKqtSCHoIx/ap/sXiuKXqD3CzZUP4t1lw/Y/qQfvo8LbJtnpY8ihhoEULXJyxpD/Z1qRVotyizBb01Yz+0KsBXsoVUY7nXKzmysT5f/PhI6f6PLfQQdOeoX6xcTcGm0r01DiTSXH22uIMvrIanxhk51+rMWHXUD4lS1rpJxvZ0imHumbQ+dBCF+FLFBfNF8MawTL7DdsRdVknyyEDDtQx8pqLnadtzTLKYhxPZHMz6m7QDWUaOT/XUY0ZNVWnFSGYUt2IOkxpzu31yplYQ/znPjsBQS8rfcT8Ty+a31WhfUKZZ+5eBmyGCeh2jUa1zvdwC6qC4ok8JukB0vZW6iWMzHoyNYfbBwdB5k8aMh6pCJd/dCtF/ujvZreJg9G0g8MF0eEJG2EeH9HOq9TWr2jOiJG6rRQxgLON0Vb9quWFRfH06qMag=",
                ]
            }
        }


class VoteToBeEncrypted(BaseModel):
    public_key_pem: str
    vote: Vote

    class Config:
        schema_extra = {
            "example": {
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAtbRRyrioFx4NuRYbh3pN\nU/p8CRSQqxd+VV45YEY12n7JKUim99wdUdKxePIRmw3rmFF7eyBOjddwycxSZ24I\ngiJXyETRh4zF4QF1iVKFNvkbJwHIXy6fy+WokVG1AwJtFqjPvEzTVFgUkJavYHGv\nw7otVLZT+2cSBAytNUhwQjTq+v76ktwRu3FV466QDo/DxijLwpMMf6TDQvhEi61m\nykrsJB3Wgn+/fueqUIVhxUffTwVXC0qyEfJ3LmSuxc+Z/GKYYUun8eKxmq9xBJUr\nRl+BJOYGQ5/pTQQD7RltZj7pgw6o4kXtalGmk7ya1v5ghoHXwGhGJv12cODJLsje\nxl922oYz2XCXgiwxiyckIRccLfBNsA3U+nE31lW+qPZyz2heJBLLJpL3v/A9xeBU\n9nXEsJ/bfsmEaOlK0Z0w+a3IKGaAVCFrIRCBdviEEdD79JiFG9c1hlG0+znCVSVD\nmxJmh3wngm6WwIH3mGUuYUrApewyl93fJqMuLVcVA2ARfS//FPWHAIkD0vT94b47\n6DAqyboC72jDsqWDdSW66mZLaFfI9djX//MdVAp3T8MMbRU/h2uX5kVQC2Au8tGH\nZnL6uVVC66tVHAgErH+sgsrQpqKBokmb7dPqFOF4ORz/kdi+JHX7edpn3GKGRehJ\nA621Hjd92Wezgt5MtNzoeW0CAwEAAQ==\n-----END PUBLIC KEY-----",
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

class VoteEncrypted(BaseModel):
    encrypted_vote: str


class VoteToBeDecrypted(BaseModel):
    private_key_pem: str
    encrypted_vote: str

    class Config:
        schema_extra = {
            "example": {
                "private_key_pem": "-----BEGIN RSA PRIVATE KEY-----\n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\n-----END RSA PRIVATE KEY-----",
                "encrypted_vote": "PBIUvoS/yo4gAnK8k+jvKmVVKPglzwIMEYxGBwVZv1iQvrtQIpiTd5fq4Ry+vG+uiiZXav8ODZU1Y7AG88mirNco4Mjt+qqDfQ9S4lQxAe4aJdOI+MIYQpg0AyzfCgQmfQMpQRnrHl9Bd7FOMUh3jCCrEwsi7xYSKGmssRpgYfFNlP7g3kxmiDcFOClu/7ZZ44nZD+WsDtNNcsSqTUJCTeZ7YlZGBX4bi98qDJufqhWFM9OklkKavMklxyKqtSCHoIx/ap/sXiuKXqD3CzZUP4t1lw/Y/qQfvo8LbJtnpY8ihhoEULXJyxpD/Z1qRVotyizBb01Yz+0KsBXsoVUY7nXKzmysT5f/PhI6f6PLfQQdOeoX6xcTcGm0r01DiTSXH22uIMvrIanxhk51+rMWHXUD4lS1rpJxvZ0imHumbQ+dBCF+FLFBfNF8MawTL7DdsRdVknyyEDDtQx8pqLnadtzTLKYhxPZHMz6m7QDWUaOT/XUY0ZNVWnFSGYUt2IOkxpzu31yplYQ/znPjsBQS8rfcT8Ty+a31WhfUKZZ+5eBmyGCeh2jUa1zvdwC6qC4ok8JukB0vZW6iWMzHoyNYfbBwdB5k8aMh6pCJd/dCtF/ujvZreJg9G0g8MF0eEJG2EeH9HOq9TWr2jOiJG6rRQxgLON0Vb9quWFRfH06qMag="
            }
        }



class VoteDecrypted(BaseModel):
    vote: Vote


# Statistics
# jednoduche vyhodnotenie
# porataj pogroupovane podla can Id a party id
# pomenovanie na predbezne (urcene len pre G a pre Admina + TV) / vysledky ()
