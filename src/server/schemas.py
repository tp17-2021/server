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
                    "polling_place_id": "0",
                    "data": "se7Yo7ZkiMkW37/n//y29IkT85ieJtFN994xo5bq6Yqx7Bl1aXaTEU+A7SvEXzYYho9A5ssRUpYlpW+6TVVc4VnG0vQzmrlIE6HCebKik5wolVk3Ha123YkRjDP3cp0XNOBIRJYuxLnLXl17vpDeiYCgQzPOMe83pjc2+9jqaUptbFYLbASEqAMHs+FoAORaAzfPS8eIBKQ/dty/Nw88XpSWuK0xthSzxhrN8la7PJ9evUoLp/yUE4KiMyniINw2oNuOPfZ6+9UQwG6RH7iHHAbxlYlAJiv85IviB8vUbeSXVgzJAAf7L/NvxYN6aQcwE6ebyVqyK4KoyZmLNXLG3OZVyBHtOpdGPJwfh5f0T8iu3DmqRNV7G9zakHZhPnkL9c9lyZUoeA6gq09WZDAwcbznqm4DVb6/cFEQm3LcSXW1xD44ONUcmLgKhk63UYtWvQSLbtpTUXk3SLaqhUGpkZ6STOH+IHXlaiFw5klW2DPQSWuC21ot8AM4oSYj8dsI1LKouFYu/4lPfFmdmDqM92Xhb879Ulk1ww18R9tLKOVohpZipkDlaEBcc4YVH6MmCSTyJ1m8pv3d8vNamrAuOiASKNJk/KDG3AN2B1ZnXQxqcdmaULYBE7tyNryDSB8pD4YB4HFKwhV4b8x05mCGDBZF1goZQ8w9R/emJ7B5CNM="
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

    class Config:
        schema_extra = {
            "example": {
                "votes": [
                    {
                    "polling_place_id": "0",
                    "data": "d24b7wm8wU6uNhOtY4JO9Nf5FeM3ThuFsytURiISkOIHwQAl/etsAxz6YEjQ61oLCi2QTtJtxmp986kB63aqXcsPlnDhcjrQK8tAxuvhIi7Dpq386lzC+bS6Gj7bTA8nRyAPVgbOo2Y9RTrYK3w2Y23iRpRexHoBeENLTeTnoRQ1X9ZDB50mc0CcEwc6DMFmL5+bYj1Q3iaFewRaEom5Cri7+1CoOKY938D24lF1CvtaPrmIJ7ziGM9/C5rq2dm51mJP+ZD+7mlTtT7iB2kUAdzEm5xMyUT+MVQPS65ek9lj6SAcA9vUmTmOb1d1C3IxTf1n0v2G9nGEGcpcaULodRbXBJHb52HNkfxCnD3C6sr/r8HzraxJS1dcpe6PMwuvqrhptMJE0/6eq08QrtyW8eEnQwoXtjbe4sM42RW9Ex4CoLbdohIqyd9377Fv555vc6ZDHneHN29TB2KmjI74SFtg8xYe5QurPq1vVFpX+qD1yUpOeN3h6h6lDMVBLvKQTWVUEYfHWnI8ojFogHq4p7NQiO6HxVkgEk7UdANyGmevW7WAEy4LC5FOhTLjsi5rFIqCbDPQlva170pC7lQYrwP42ugY/qkevJ8xaKNuG3nkbqU9KS1v6kBQh0Z01ayv9/agsJ/8i073BtcmUlhgiedK06WgBp8Ilexv5dt3KtU="
                    }
                ]
            }
        }



class VoteToBeEncrypted(BaseModel):
    public_key_pem: str
    polling_place_id: str
    data: Data

    class Config:
        schema_extra = {
            "example": {
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAw7d1huCqarX4Cd5E5Iyw\nZIam+QVdf6qg9WBwcT1oBoZtns0KAFMUUGWrKTBpm3Vr/rg1n60KaP2HNMuGeJl9\ncbV3KIOL8lmj5KdM9B3sZB6u5VFSw2Utpka8ro2CxYw+IaGLi6ZWHsMWbikhUFGi\nIiXHKvfYHnvVkK6U6tg4g2MYE/8lgXh/TI1fmPbgMyqDrh2jLDtlJXxc00b8qS3Z\nQOLb8ABgxejjXdDWN7fKJIXDF8cETOh5hKFYWRJCps8vFz2aqiPHpXlWUwtRF46V\nNJEnTjLT9q4/E/KDyqmYvqSC2cbEaMoMjZ4Yo8+jKIH+berZp+gHr79mxar0zJJ4\ncmOEQMptABi5othXQnIbKIjH//PVkjQpO3XreTl+0zFAmfFWozO0DSxrLNiizko7\nLpugdIxAjnz3mOGQWh6LCb+VeD6es2Qiufa0M1ALL+aYaIdTCKYHQj2wAQT8691t\nkstofK5wncsgoojEF0o5JpimElpHvz2Slyj4A8mKR+4FeQ3Ytda0IaD7MaW783DM\nRjYV23a5e5EQU+vHtxOwMQN/U4a48dNsGdMm4x7HuszcJW3xVmd/Oa6bfm9preMQ\n0ABZn4blVEGDbGiVsPQ9OL7X001ckC7cdMoT5g0pd7RQrH8B7j2dbYRcIAfUj94l\nfxuyzOFKA3RzPneKCkyHFw0CAwEAAQ==\n-----END PUBLIC KEY-----",
                "polling_place_id": "0",
                "data": {
                    "token": "fjosjfidsw",
                    "party_id": "10",
                    "election_id": "election_id",
                    "candidates_ids": [
                        "1158",
                        "1077",
                        "1191",
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
