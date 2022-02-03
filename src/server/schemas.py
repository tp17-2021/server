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
                    "YxRlxRHzAmUONEn67eQO3cj8q7HG/XCD6t7lB5tN8C0Vaj6pTegyxwGiIMLze1fsd9iSKOfyJ9M3CmrZ3g+t+Z9xWf7Ysl6ES2vXG4+gWYIyacOX1pWx+eyX7ngTXZIJpwzn6l9Qm+6Iu8rMqb0UFf8fFwmiEN7LDXeN0j6N0ItSv67gh5jabyQvBKlMDVeiBVY8U1geD0YPLGdXcVgRTmnduaowTDL7WDiNpF2hrZ1JHCvcuT0A24OccOBmV8/1hisodN2Kfyekhc7r2ddQEsdvdjcX0/kmviMRGzbNBl8fpnSS5sWUkWl86qRxV6krOuS4Vhy4YT7ZEqx/46DqYYuc3QKrWRciR9KQhoBj/Gq8X9kCT7DO9QhFn6hBDLdnLo5Y4KDa+tCYMskHPBeHMtpZMqM61fi0cd4qT7gJM9zjBVlw7v2CwnbZa/DccXshkU0Dd2t2zuDIguZ9HptWstdTy3+1dSxB3sICjhoe9v0rDc3QirQwalbk7wuEQAqoitUznqGLsQIfB1OO3uJOpW6vT6htKR7aPuy/IcmYKf2aqKl+DTYGCA6tvIH7CG544mVp+UjhuLLgk79xT5ExRHhn4aaybk2jOMTrTpavDPsBQshaHEaPNTZCRqe1jUF3l/frDo/FasI/WKIg1efJMgvGa+ADADI4k3+ACppmS0eJapxKt9fzL4IOZaEB35EYR/v452+1NysehMokvgmZhWDRRXCh4TvK2ANIyPOqHyl2r8swGmeV2Ps+J6KXIMyVkbBJLowO+qF/4zdXqPkbepunsAfsOdJNzv+LAoCi4ZuLQ6o0iX4cbJAEZZz2CNyIcyVqn2kJdbllQOZvs+N4rAsdHZiq4mR6Cbmpqd81qbBh7qn6Fs6jkGHuWKvrcBdtZ+XdaxErywkxTbBSuFYfF7I+HxfoXn5cT4IrNuoSqsaC+AN8GT+toiEqLBLV+uCb13R4JN7bEsNWijxDxb2zVSKtfHCOt7ksVsOaPaNRbbCpLaKoXGWvQorQ7EvW6hPdtC3oEx6+EmprfQYm10Y0u+/nQfTLDm9in0XhQ+Vj463UNz90sJ+2Qf0GgxAnQ7jf1Ff9ebIWZqIPQFWNHPnMMFOuyr38bd8JvaErHvexd86sZi0LjD3uJWCloP1R3uTJcIutLggmRs8zl6FCb/H1jsBt4xlnM/sfoxoYfBTD94U7mAqmU4bGKBi5QvMDqH3Tk9yHLTBGhR62CGbkWIi3z5gUJqy7NCjcFoZGmVB2EtcZjjAad3zJdxIzG1BKUbcxKtFUMi6MqgYNM0KPcd6AwxQfGFN6kC3ycMM29zL4z4cQqIVKS+O6ngn8mL0Gijts1eIIVyMKSDNtITa4BF9MfA==",
                ]
            }
        }


class VoteToBeEncrypted(BaseModel):
    public_key_pem: str
    vote: Vote

    class Config:
        schema_extra = {
            "example": {
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIEIjANBgkqhkiG9w0BAQEFAAOCBA8AMIIECgKCBAEAuS4955lYO5Dgj0rnxH1r\ncluAdGoN63f1GsO0MJMmJqkRsyOyqKbQ0e6hmRfY5G0oqlim8+9oRRVD4KMrR3JB\nVleghL9WOqr1Pp5luWkg59WyMXI1A1pWbW6XrAGcyco+9RkB0qS5CWEPZjCU4+g0\nmnKQESRJzg/KoiBMq5seOtpryg7+Hdbz6pNXmpg5wKmroKj6+L4EO/5GrEbcvHhe\n1axPwbCLxpjXxMydfiVyATQJCgfqQd6j80TCM1QjmNNNplnlBVYwLkul0S352HbN\na7OrGLuOm2A0XOj9d6+ZDH++NYmv4s0nz7Jp/ujHs+f1fCmenOewJFfMJdzkSKOJ\nuS4kkPUj6OK3lWc3nXjexCRTmwxKXPm2pSG67zv/FWK85HI62ZMTobWKLeQI/BmB\ntuS3Jth3jTk+7HUzf/jCQIZoDYNeJyKrOIXRQd/EAjFDoLlfYjwplRIQfPlV1dwz\nlFNl1Sqm90iTIqdTc6nl4RhP4mk1OYS//SSXvTTw3YqBETxM7QGn4ojvc4QzpDXi\nkN6lJ9JRpNbdH66/tPY/kY4AOzAepWLbAzZls1qNPbL0SImBPi272O+LJm85SouF\nl3g78aZgWNbD+biCQN1mBtTxbI+8YYKG4QqNkIYIiCI8K7cOEZYT2Jan+rjhiMSy\nRkNlFBueot/zQPGqGko17vDjEWfWQ3OtG8QXzJHf5XFdhNoycSXZOUqiHwUTWP4c\nZu0tfM08fwEEXUKrkg6VEKEc7j9U2rZXgeq7XEl8lxKdi9ORuAzLNoDzSC+zdguQ\nkumTlJ69cxi92igOo9fynBKPEX25oWxIrjKqwnXP3NKGHePQ0o++Eo0Cqdg82Zuc\nb92y0kzVZ5dVKBRLJ3LBKIqF8JgEUYpY/jIue3Nexvj0N/jWoV/woe77Ho9tMhiH\nhlNXnAJrsPShlVkpBqw+uKqZaVvBJbPt2EpdU3GYnSuR7ye/QsXdk/9jdfdBqLcL\n53qA0S2j/B25Z0uuvCr43G3ed6mE6KvxFCuGZ01RGjD4Stz/1iBgcWnPhtNExlhf\nOuHKf6C1j5dkZQCv7i37UdaH7t+VnXMuG+xM21hMV7mv3OglC+E9Gt3dD3MZSe4/\nUe611/yBrZSd2VZiPV6IkZOAgojTv5tRpu/mpdRUvPC5YnuoNVj5NkwCcYFQjnJq\nQVgFnceZcg4eBI5013a/HVcyaMkXVb/SMCeJQ9Suoqjnc0599jcaxJ739d0YJEHh\nNaBJmrYCHUtr5N9IKTIg2tT2YSZj8SpZgwgSqN5AjeS1kcZQ192VHUGTdHGKKYiA\nHAwgHISAdqHx3/D8TGYEbTGF/hQCvM9YAn7P/waO+KALR0E9h1gZYOR4aGo3IUYd\nfQIDAQAB\n-----END PUBLIC KEY-----",
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
                "encrypted_vote": "YxRlxRHzAmUONEn67eQO3cj8q7HG/XCD6t7lB5tN8C0Vaj6pTegyxwGiIMLze1fsd9iSKOfyJ9M3CmrZ3g+t+Z9xWf7Ysl6ES2vXG4+gWYIyacOX1pWx+eyX7ngTXZIJpwzn6l9Qm+6Iu8rMqb0UFf8fFwmiEN7LDXeN0j6N0ItSv67gh5jabyQvBKlMDVeiBVY8U1geD0YPLGdXcVgRTmnduaowTDL7WDiNpF2hrZ1JHCvcuT0A24OccOBmV8/1hisodN2Kfyekhc7r2ddQEsdvdjcX0/kmviMRGzbNBl8fpnSS5sWUkWl86qRxV6krOuS4Vhy4YT7ZEqx/46DqYYuc3QKrWRciR9KQhoBj/Gq8X9kCT7DO9QhFn6hBDLdnLo5Y4KDa+tCYMskHPBeHMtpZMqM61fi0cd4qT7gJM9zjBVlw7v2CwnbZa/DccXshkU0Dd2t2zuDIguZ9HptWstdTy3+1dSxB3sICjhoe9v0rDc3QirQwalbk7wuEQAqoitUznqGLsQIfB1OO3uJOpW6vT6htKR7aPuy/IcmYKf2aqKl+DTYGCA6tvIH7CG544mVp+UjhuLLgk79xT5ExRHhn4aaybk2jOMTrTpavDPsBQshaHEaPNTZCRqe1jUF3l/frDo/FasI/WKIg1efJMgvGa+ADADI4k3+ACppmS0eJapxKt9fzL4IOZaEB35EYR/v452+1NysehMokvgmZhWDRRXCh4TvK2ANIyPOqHyl2r8swGmeV2Ps+J6KXIMyVkbBJLowO+qF/4zdXqPkbepunsAfsOdJNzv+LAoCi4ZuLQ6o0iX4cbJAEZZz2CNyIcyVqn2kJdbllQOZvs+N4rAsdHZiq4mR6Cbmpqd81qbBh7qn6Fs6jkGHuWKvrcBdtZ+XdaxErywkxTbBSuFYfF7I+HxfoXn5cT4IrNuoSqsaC+AN8GT+toiEqLBLV+uCb13R4JN7bEsNWijxDxb2zVSKtfHCOt7ksVsOaPaNRbbCpLaKoXGWvQorQ7EvW6hPdtC3oEx6+EmprfQYm10Y0u+/nQfTLDm9in0XhQ+Vj463UNz90sJ+2Qf0GgxAnQ7jf1Ff9ebIWZqIPQFWNHPnMMFOuyr38bd8JvaErHvexd86sZi0LjD3uJWCloP1R3uTJcIutLggmRs8zl6FCb/H1jsBt4xlnM/sfoxoYfBTD94U7mAqmU4bGKBi5QvMDqH3Tk9yHLTBGhR62CGbkWIi3z5gUJqy7NCjcFoZGmVB2EtcZjjAad3zJdxIzG1BKUbcxKtFUMi6MqgYNM0KPcd6AwxQfGFN6kC3ycMM29zL4z4cQqIVKS+O6ngn8mL0Gijts1eIIVyMKSDNtITa4BF9MfA=="                
            }
        }



class VoteDecrypted(BaseModel):
    vote: Vote


# Statistics
# jednoduche vyhodnotenie
# porataj pogroupovane podla can Id a party id
# pomenovanie na predbezne (urcene len pre G a pre Admina + TV) / vysledky ()
