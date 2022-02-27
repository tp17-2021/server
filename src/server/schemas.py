from typing import Collection
from pydantic import BaseModel, validator, Extra, Field
from typing import List, Optional


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
    id: int = Field(..., alias='_id')
    party_number: int
    order: int
    first_name: str
    last_name: str
    degrees_before: str
    age: int
    occupation: str
    residence: str


class Party(BaseModel):
    id: int = Field(..., alias='_id')
    party_number: int
    name: str
    abbreviation: str
    image: str
    image_bytes: str
    candidates: List[Candidate] = []


class PollingPlace(BaseModel):
    id: int = Field(..., alias='_id')
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
    id: int = Field(..., alias='_id')
    polling_place_id: int
    private_key_pem: str
    public_key_pem: str
    g_private_key_pem: str
    g_public_key_pem: str


class VotingData(BaseModel):
    polling_places: List[PollingPlace] = []
    parties: List[Party] = []
    key_pairs: List[KeyPair] = []
    texts: Texts


class Vote(BaseModel):
    token: str
    party_id: int
    election_id: str
    candidate_ids: List[int] = []


class VoteEncrypted(BaseModel):
    encrypted_message: str
    encrypted_object: str


class VotesEncrypted(BaseModel):
    polling_place_id: int
    votes: List[VoteEncrypted] = []

    class Config:
        schema_extra = {
            "example": {
                "polling_place_id": 0,
                "votes": [
                    {
                        "encrypted_message": "36AMNvcpAWdHAXKCSWexgyjxrt7xeWwhOf+oUMBqip/C051EZWlN4N4x3hVPwwIQh/l78suUNYYYQBTkERPkuaZ40D1NV4LM7nb+DHcQ0nzGIFxHND3CIDkT9UOi1AmrqrCtyVMpDP1SI/2glHjbMsrw9VowA3L8hbf3U4wSF65ocF5IxN8mrOraXUopMcu+GgFKjBh3Y56yhZfxwr7go2YvQwph1HuLYVkkBi3ZAk+1DHCuQ+oQC3ivVJPF6SBOHPJIgLGM5NUsJwq5MUWSgxlr+iQI/g/uWbjkcS7M9uBZE6+QRTD++6sqZhHxc8RTLVtqAmrp0m1We6kf/Nrx7KdqagpHQz1vgZEf50L+kVgXf9PnX1THB7U+jVB0ogvM1fmZ+JvWURHt9ZhgdO1wZvzigQP6jTNZw5amzga2T+6/KwC47dxdnnT/l/fSBXzgAbsCNWCegJfTakvpsCNjWRlPKIvbPcGEIZDKBaMTz/zhKHqTgQV/f3qmlHgq+GYVPsyl95NVBFiiYwWxYWvJIl8RCREfx39t2bAx74YsJ4fT8G3u438l6BvT5DMrEbN3YlAS7gwuRt4j3AQUWmyzHesIW1o/pJd+5IpNYQ3ld6363iu5G4mC00lnImnSig==",
                        "encrypted_object": "lb5B/LAg2/38mot9jYzRpa9O6YwrXDilpspPrGrnTKKYUXVfQ9JhW5JIGoP6FuQBXM2XzlcXkb90/VDK6+h/HeJKEUf81h/A/KiN4AZVBtRoHXOpq1gyRpFk7q5dhHzniStAPZOLruNtrAYmOoUNq3hmHLxs2KnRTMZiEc9kOefIS1vjPKFAClNCqKL++7orwvRPWGzmLMPbq6DFc/Sb7hXVlBMiUCmS2iMtz9mgs9IXheCqvcGYZQZOubFK3zjtqOvFEjuGACUZkuGbmxHEFgbBMCUPXOH933aP8eNY33+UIKSc2DSNKTOOySJNi3EolJmUhbQT5NIWXf9lE3jqXg=="
                    }
                ]
            }
        }


class VoteToBeEncrypted(BaseModel):
    vote: Vote
    g_private_key_pem: str
    public_key_pem: str

    class Config:
        schema_extra = {
            "example": {
                "vote": {
                    "token": "fjosjfidsw",
                    "party_id": 10,
                    "election_id": "election_id",
                    "candidate_ids": [
                        1158,
                        1077,
                        1191,
                    ]
                },
                "g_private_key_pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA1ZTVl1y9Zh2ZJ0EOW8eo+2EFBBRiHoDJazdLO+dckpHDpwwQ\nLmwKquZqVhCogUQmIHJZ6b6QlFcxX0fTvizF0SsocvKeJ5orgaMeC2kjkgf1gMec\nwRDkn7tFhoezQ8xYGhlcZVho9CzBJKNmmDohqkWpgguAOQnEzt07c2o5drH03km9\nnF1Nbsu/B05CozK3LRC+mnZUowNwtzQV7tPAYLshpK+awmJ8upqAwy+7JHXPfVz/\nbeShMuMXxGi28jUYe5rGLWrO73xbkxMkI+dK0Gxym0UG1LodR9hp+EmWoem8HJqY\nE5L1HhqJCy8bNP+5EeXFhaohRfMhMcWE9AInswIDAQABAoIBAGZLg8WcQIaRNJJt\ngVAKH/BOdpWOobQUYOQ+NoV5eYgl0nzGtVVWoAFcnJ+eGObY2h3+RvxCLoMuA9Kr\n10mlrhVRw2zSsVcsaxwLIU+7yrKdp0NH19dMnQO4MUOO6RhW3feaH/vWTWZtrRA8\nRt4wMYGZHefQVFh9Skr+AQR1YxJqpvNAahOJuAkoK5wkMtOmDQFI9VYPARFH1tSL\nE1Rf9aQ4Y2ZGffZsr9i1adzrX0uAPFpXH5EZVwYx5hr/HPfP3xgiZ9aP4kJjHTwp\n4T1k5KYHN9mH6oQccGi9GNOPGZQagtid/g6IsWIgdiVOWyjoNT8jWBQLa7Kl57n6\n4x25uJECgYEA2xXcj1zxc1wjJpVDN7mOStbrk9ngLZRhU34UVxzCugbMFesBRO9X\n39u7t80D6Q7cJ9JE4LrBTYJd736k5oFp3Hzea4jmD4zPUKSRR8BD5dQ7th/XOcvo\njaEyoWD0kWblTqkAinfoKzt4HxEsBBAsIh0PyhgWz4yoBuI0LZgX44kCgYEA+ZGP\nWbfXm9ZrMWU3Owhdqr3J1YqJKNMa+ydQC2xxnv4LAbiSnKyAGACiAP8ymKceU0bA\nHtQUaLoYeMEJcJ6fSK9xFcrUB+VRxmvcG9zrwoYUjRMxSPoMh+r68vzGCpQ7ZcSQ\noLd67ncWD1X2uPeyqex83N+e++ih5q2IcUwillsCgYB3A89HikQYWQs3YIqdcQ3d\nlhdvwEJKQHsGsk02bYdTK3IezgVof2ULVQEK/jKLnuj2MQH92zY7dwC0o+XM2qy5\nfJQPctUXyXSt6FiL0+SOq9asP2vaF+2DUviANn1lp7IWIzUKA815/tpodhmlM2vm\nNEdpj+CEa3K0Gpoh0qfXkQKBgQCCwOB6APfVjeFbX8wwAZIRgp3cY1i5KuFX9KDb\nW1WsFy1tGWa27ymtaad3Hj1D/UrGFqtRe4u10so/eeOYPYL2cfStljbAbEUL0Dbh\n4j0jDVx3DTclJNyr2VDhPc4EfOUhzHp5uaeOiJXmMwOwpRXWMTC6B+8jzB4G3aQ+\nt8TnQQKBgQDCLjDCEc/l3KHQYfTpxX1EIvoqEJSIRUyXjuICj0kP+fBXcWiYEEd4\njJTryVRmIulyJTuxAhhBNXlHGIMPX2fmU7IGgRKO/2kvb2yLGTnfecUGwPL4YEGy\nw0yCPjyhu9/fpr1lDUJ0NN+GmpqplkqvXtYPLdJSIigDVW7Jn/stRQ==\n-----END RSA PRIVATE KEY-----",
                "public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs6lvNfr+Eo6Mt+mW95fh\njUbCRygCNok8Y8yIu502lpDiz3bNdR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7I\nEpRSmY1nElabMoBbU2vsPWBsu7WR31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPu\nRVtuHy/q2tD5sY2ekWJc1YsoeQ5JDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c\n2P4NpNgSJ2NT8aF/bDbu3sQk9QuQXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchq\nrYj5Xnql/wcrnyOhcgeKsOBieH/fETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG4\n7QIDAQAB\n-----END PUBLIC KEY-----"
            }
        }


class VoteToBeDecrypted(BaseModel):
    encrypted_vote: VoteEncrypted
    private_key_pem: str
    g_public_key_pem: str

    class Config:
        schema_extra = {
            "example": {
                "encrypted_vote": {
                    "encrypted_message": "ZiwaJl+BScLyGgpGqOu4jSG/MJ4vtgCYm4f6j5xh4TThD49y972z9bWALEe166HZzgKpqsBD36Vbstvd0VL8FeEF8TttOZWrBo1uT6c7d2Z5EzHWPAE5oScYwZ4288s8XJ+dHQv8h9dXpEaxGtKG/mzz3mhNh3oUwZ3T2DvlyUTEeMsD363XVpsyZy47je4mKEWBfEZgoC86OI6pYJ0Ckcxa5X0D7eql5ElzEHfVSpXr1LOh9DLzC+Hrj1oIIcYKSsw0uf275Pk+E1B34kDr+pePgBvRQIwQzXZP5KUPSil5U7qbiNjUy0M9Ztx1FZB0/YUux46AhHQdQhvDQ6gWeSlYV4tCJaKD+KTRqaLMUSZknOJLmWn1Ci1s95NIBlwP6izyhnCLPaiNaKdxmbbYOU6u6eBQ0ZRKS3ibW6s/tqtazfznF3fLdl6sn0KS7Yknkcg8Z3b7QSjrzcOsEhzw62AtblSUma7+mH3PXqDmXyuNjh1SG9ShbYA5CKdOmZZ6ksm8MWkfjtIiifN9bC+vgy7NuqWtdgfbb7CiqCMTm67/p2yG2wQEwsYEMbDc0LAYrfR5qtRxxy5bTdSXZWLXPcueS31tblkkMOW7BIk/dZCGeiSsFZ1wJOataPOlMg==",
                    "encrypted_object": "oN59MQBwMNsdeABCNQt/I8DsDYLx3VdaIIGcBn06VhKArg/aTU5uomXkZs0+8Apm3ELYtHmNWeqpTms26PcFcyViEvFaylAja12ic5qs71Fg3LKzbXu1kB7SgBqDGcXQL2iAuaoBuLlrrTm0dJ69spduSekM/PUWWJwh5wTsMHGGoPJd2BgzwO2R+5RTEaeM733+D5/BYMbXlsOFfyfDhD4B8u297/hVAGLtHq666gHGJREsuaj+wzNx7JqB+PBGCjJa0CE519txpaztU9N9QMMuVwn/J6QHUbOTJk/KVDxcmWD6L9wAal00jwEnT7R9XlhOLJx4rdtxqfZ6ZNC7Jw=="
                },
                "private_key_pem": "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAs6lvNfr+Eo6Mt+mW95fhjUbCRygCNok8Y8yIu502lpDiz3bN\ndR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7IEpRSmY1nElabMoBbU2vsPWBsu7WR\n31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPuRVtuHy/q2tD5sY2ekWJc1YsoeQ5J\nDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c2P4NpNgSJ2NT8aF/bDbu3sQk9QuQ\nXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchqrYj5Xnql/wcrnyOhcgeKsOBieH/f\nETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG47QIDAQABAoIBAAEotU5QfGpm8gUF\n/64cOMs1Bm/4E+QmCFrF5IQ1VFvlBBmQGZGko6i6AHR0CtCN2OuVAne9sTtfYyjU\nLvPdzUcMQ3q40+B3n5BB6UvFZ2SIiu1RE3nDCRyFx/VWATEqwZKTmaEUsO1BMHwx\nJWW5+K4tb1HunUZ20M2OEfkps39438Vk1R4I/kJqhp8E7mLYshBHyK1OwOgiInE4\n1Z2SwAhvGKnNE3TnBlV7/K5XFQg3b7QWORHvlvnNHU7ed8TXmizp7No6Qxl1ZJ2z\nier3f+XiMAryIb7AyBJyIWGnQllrDhff5hhNObltLmmaAkQm3LSsJ52GU9e4i/6c\nF/sshLECgYEAu78IM4Sj3D+wd6lMNVInU7Np8o8L5Ihq9Y1ccHmyvbVdxeGPIfKo\n/j/WwoCQJPKFQJLjQru3s1nVOOYNE5/CUQEEeFguzRL43UtzywONc1+L4a2MOnqO\n8ywQF1OrxByFy9eFLdN5ETdDhriajx8VM0hRrmeLsiGcmVZet1lFjjkCgYEA9PoD\n3x2qaCrTe3mZPHzfayHYWVFFxvRYOjxmIbOdzQZPeQA1tXEHyHnY/z3ibA+v3iQu\nQ2n5RQM4/+ItjS2xrwL+hlU3yue67HfBuUyFcFjhEUu0sdN4439d3K9hAeX7eTfB\nZ2CsNieqPxYZj6tSL4+0Fru4o4VpD79u7pSlgFUCgYAdWiJoG4aauoJWUuuNMojf\ndx9LQr3zPriqJy2akAw3yJEejMMZ5ZwyE7z5r6vZeukGTXCmUD7KFXNWb/D/bmys\nyWHvhqnaeerafh9eT/HfZcKyx7Uyt1J+BheF7hjeki8AzXMO1Q8Kd/9gop/XXF6u\nI9JRV/LpKIQZHP214IkVUQKBgQCpqO09fIIkGmTUwuZJagIhZBM96Hd2zoq76lCh\nTpAfChvIJUkNG/bT9O8/9k/1nveh1VTlA2PLU+wJ606408iW+G/mAObe85YVZusX\ntdNEd4mIPPIrpdW3WOJckGmSswBydxbOzbj22Imjn16cjX4hylhi1ieNuDuG2IGv\nYess8QKBgQCrT1ATnUxqacw/x8RRJpZWV4rnrkujA2XPLu4YaMODzVSkk+HVEabH\nJtA4AV6O0bneAgywBltg9wL0L98Q6ckuEo6hA9rskvwxQAk9uawJDzy1Bq/aEcSD\nu707LpYyMboRA/+1Sw8GEYF1iKdVJnGN1pjse4V4mJvobPPEZ+4Atw==\n-----END RSA PRIVATE KEY-----",
                "g_public_key_pem": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1ZTVl1y9Zh2ZJ0EOW8eo\n+2EFBBRiHoDJazdLO+dckpHDpwwQLmwKquZqVhCogUQmIHJZ6b6QlFcxX0fTvizF\n0SsocvKeJ5orgaMeC2kjkgf1gMecwRDkn7tFhoezQ8xYGhlcZVho9CzBJKNmmDoh\nqkWpgguAOQnEzt07c2o5drH03km9nF1Nbsu/B05CozK3LRC+mnZUowNwtzQV7tPA\nYLshpK+awmJ8upqAwy+7JHXPfVz/beShMuMXxGi28jUYe5rGLWrO73xbkxMkI+dK\n0Gxym0UG1LodR9hp+EmWoem8HJqYE5L1HhqJCy8bNP+5EeXFhaohRfMhMcWE9AIn\nswIDAQAB\n-----END PUBLIC KEY-----",
            }
        }


class VoteDecrypted(BaseModel):
    vote: Vote

class StatisticsPerPartyRequest(BaseModel):
    party: Optional[str] = None
    class Config:
        schema_extra = {
            "example": {
                "party": "SME RODINA"
            }
        }

class StatisticsPerLocalityRequest(BaseModel):
    filter_by: str
    filter_value: Optional[str] = None

    @validator('filter_by')
    def group_by_only_plausible_localities(cls, v):
        possible_values = ['region_name', 'county_name', 'municipality_name', 'administrative_area_name']
        if v not in possible_values:
            raise ValueError('Invalid filter by value. Possible valuies: ' + ', '.join(possible_values))
        return v
    class Config:
        schema_extra = {
            "example": {
                "filter_by": "region_name",
                "filter_value" : "Prešovský kraj"
            }
        }


# Statistics
# jednoduche vyhodnotenie
# porataj pogroupovane podla can Id a party id
# pomenovanie na predbezne (urcene len pre G a pre Admina + TV) / vysledky ()
