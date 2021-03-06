# General modules
import asyncio
import json
import motor.motor_asyncio
import os
import random
import string


async def get_parties_with_candidates(DB: motor.motor_asyncio.AsyncIOMotorClient) -> list:
    """ Get parties with candidates from database """
    pipeline = [{
        "$lookup": {
            "from": "candidates",
            "localField": "party_number",
            "foreignField": "party_number",
            "as": "candidates"
        }
    }]
    parties_with_candidates = [party_with_candidate async for party_with_candidate in DB.parties.aggregate(pipeline)]
    return parties_with_candidates


async def load_json(path: str):
    """ Helper to load json file """
    with open(path, encoding="utf8") as file:
        return json.load(file)


async def seed():
    """ Seed data """

    CLIENT = motor.motor_asyncio.AsyncIOMotorClient(
        f"{os.environ['SERVER_DB_HOST']}:{os.environ['SERVER_DB_PORT']}"
    )
    DB = CLIENT[os.environ["SERVER_DB_NAME"]]

    random.seed(1)

    await DB.parties.drop()
    await DB.candidates.drop()
    await DB.polling_places.drop()
    await DB.votes.drop()
    await DB.key_pairs.drop()

    parties = await load_json("/code/data/nrsr_2020/parties_transformed.json")
    for _id, party in enumerate(parties):
        party["_id"] = _id
        await DB.parties.insert_one(party)

    candidates = await load_json("/code/data/nrsr_2020/candidates_transformed.json")
    for _id, candidate in enumerate(candidates):
        candidate["_id"] = _id
        await DB.candidates.insert_one(candidate)

    polling_places = await load_json("/code/data/nrsr_2020/polling_places.json")
    for _id, polling_place in enumerate(polling_places):
        polling_place["_id"] = _id
        await DB.polling_places.insert_one(polling_place)

    polling_places = [polling_place async for polling_place in DB.polling_places.find()]
    parties = await get_parties_with_candidates(DB)

    number_of_votes = 10
    votes_to_be_inserted = []
    for _id in range(number_of_votes):
        vote = {
            "_id": None,
            "token": None,
            "party_id": None,
            "election_id": None,
            "candidate_ids": [],
            "polling_place_id": None
        }
        vote["_id"] = _id

        selected_polling_place = random.choice(polling_places)
        vote["polling_place_id"] = selected_polling_place["_id"]

        selected_token = "".join([random.choice(string.ascii_lowercase + string.digits) for _ in range(10)])
        vote["token"] = selected_token

        selected_party = random.choice(parties)
        vote["party_id"] = selected_party["_id"]

        vote["election_id"] = "election_id"

        selected_candidates = random.sample(selected_party["candidates"], random.randint(0,5))
        for selected_candidate in selected_candidates:
            vote["candidate_ids"].append(selected_candidate["_id"])

        votes_to_be_inserted.append(vote)

    await DB.votes.insert_many(votes_to_be_inserted)

    polling_place_id = 0
    private_key_pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAs6lvNfr+Eo6Mt+mW95fhjUbCRygCNok8Y8yIu502lpDiz3bN\ndR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7IEpRSmY1nElabMoBbU2vsPWBsu7WR\n31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPuRVtuHy/q2tD5sY2ekWJc1YsoeQ5J\nDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c2P4NpNgSJ2NT8aF/bDbu3sQk9QuQ\nXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchqrYj5Xnql/wcrnyOhcgeKsOBieH/f\nETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG47QIDAQABAoIBAAEotU5QfGpm8gUF\n/64cOMs1Bm/4E+QmCFrF5IQ1VFvlBBmQGZGko6i6AHR0CtCN2OuVAne9sTtfYyjU\nLvPdzUcMQ3q40+B3n5BB6UvFZ2SIiu1RE3nDCRyFx/VWATEqwZKTmaEUsO1BMHwx\nJWW5+K4tb1HunUZ20M2OEfkps39438Vk1R4I/kJqhp8E7mLYshBHyK1OwOgiInE4\n1Z2SwAhvGKnNE3TnBlV7/K5XFQg3b7QWORHvlvnNHU7ed8TXmizp7No6Qxl1ZJ2z\nier3f+XiMAryIb7AyBJyIWGnQllrDhff5hhNObltLmmaAkQm3LSsJ52GU9e4i/6c\nF/sshLECgYEAu78IM4Sj3D+wd6lMNVInU7Np8o8L5Ihq9Y1ccHmyvbVdxeGPIfKo\n/j/WwoCQJPKFQJLjQru3s1nVOOYNE5/CUQEEeFguzRL43UtzywONc1+L4a2MOnqO\n8ywQF1OrxByFy9eFLdN5ETdDhriajx8VM0hRrmeLsiGcmVZet1lFjjkCgYEA9PoD\n3x2qaCrTe3mZPHzfayHYWVFFxvRYOjxmIbOdzQZPeQA1tXEHyHnY/z3ibA+v3iQu\nQ2n5RQM4/+ItjS2xrwL+hlU3yue67HfBuUyFcFjhEUu0sdN4439d3K9hAeX7eTfB\nZ2CsNieqPxYZj6tSL4+0Fru4o4VpD79u7pSlgFUCgYAdWiJoG4aauoJWUuuNMojf\ndx9LQr3zPriqJy2akAw3yJEejMMZ5ZwyE7z5r6vZeukGTXCmUD7KFXNWb/D/bmys\nyWHvhqnaeerafh9eT/HfZcKyx7Uyt1J+BheF7hjeki8AzXMO1Q8Kd/9gop/XXF6u\nI9JRV/LpKIQZHP214IkVUQKBgQCpqO09fIIkGmTUwuZJagIhZBM96Hd2zoq76lCh\nTpAfChvIJUkNG/bT9O8/9k/1nveh1VTlA2PLU+wJ606408iW+G/mAObe85YVZusX\ntdNEd4mIPPIrpdW3WOJckGmSswBydxbOzbj22Imjn16cjX4hylhi1ieNuDuG2IGv\nYess8QKBgQCrT1ATnUxqacw/x8RRJpZWV4rnrkujA2XPLu4YaMODzVSkk+HVEabH\nJtA4AV6O0bneAgywBltg9wL0L98Q6ckuEo6hA9rskvwxQAk9uawJDzy1Bq/aEcSD\nu707LpYyMboRA/+1Sw8GEYF1iKdVJnGN1pjse4V4mJvobPPEZ+4Atw==\n-----END RSA PRIVATE KEY-----"
    public_key_pem = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs6lvNfr+Eo6Mt+mW95fh\njUbCRygCNok8Y8yIu502lpDiz3bNdR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7I\nEpRSmY1nElabMoBbU2vsPWBsu7WR31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPu\nRVtuHy/q2tD5sY2ekWJc1YsoeQ5JDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c\n2P4NpNgSJ2NT8aF/bDbu3sQk9QuQXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchq\nrYj5Xnql/wcrnyOhcgeKsOBieH/fETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG4\n7QIDAQAB\n-----END PUBLIC KEY-----"
    g_private_key_pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA1ZTVl1y9Zh2ZJ0EOW8eo+2EFBBRiHoDJazdLO+dckpHDpwwQ\nLmwKquZqVhCogUQmIHJZ6b6QlFcxX0fTvizF0SsocvKeJ5orgaMeC2kjkgf1gMec\nwRDkn7tFhoezQ8xYGhlcZVho9CzBJKNmmDohqkWpgguAOQnEzt07c2o5drH03km9\nnF1Nbsu/B05CozK3LRC+mnZUowNwtzQV7tPAYLshpK+awmJ8upqAwy+7JHXPfVz/\nbeShMuMXxGi28jUYe5rGLWrO73xbkxMkI+dK0Gxym0UG1LodR9hp+EmWoem8HJqY\nE5L1HhqJCy8bNP+5EeXFhaohRfMhMcWE9AInswIDAQABAoIBAGZLg8WcQIaRNJJt\ngVAKH/BOdpWOobQUYOQ+NoV5eYgl0nzGtVVWoAFcnJ+eGObY2h3+RvxCLoMuA9Kr\n10mlrhVRw2zSsVcsaxwLIU+7yrKdp0NH19dMnQO4MUOO6RhW3feaH/vWTWZtrRA8\nRt4wMYGZHefQVFh9Skr+AQR1YxJqpvNAahOJuAkoK5wkMtOmDQFI9VYPARFH1tSL\nE1Rf9aQ4Y2ZGffZsr9i1adzrX0uAPFpXH5EZVwYx5hr/HPfP3xgiZ9aP4kJjHTwp\n4T1k5KYHN9mH6oQccGi9GNOPGZQagtid/g6IsWIgdiVOWyjoNT8jWBQLa7Kl57n6\n4x25uJECgYEA2xXcj1zxc1wjJpVDN7mOStbrk9ngLZRhU34UVxzCugbMFesBRO9X\n39u7t80D6Q7cJ9JE4LrBTYJd736k5oFp3Hzea4jmD4zPUKSRR8BD5dQ7th/XOcvo\njaEyoWD0kWblTqkAinfoKzt4HxEsBBAsIh0PyhgWz4yoBuI0LZgX44kCgYEA+ZGP\nWbfXm9ZrMWU3Owhdqr3J1YqJKNMa+ydQC2xxnv4LAbiSnKyAGACiAP8ymKceU0bA\nHtQUaLoYeMEJcJ6fSK9xFcrUB+VRxmvcG9zrwoYUjRMxSPoMh+r68vzGCpQ7ZcSQ\noLd67ncWD1X2uPeyqex83N+e++ih5q2IcUwillsCgYB3A89HikQYWQs3YIqdcQ3d\nlhdvwEJKQHsGsk02bYdTK3IezgVof2ULVQEK/jKLnuj2MQH92zY7dwC0o+XM2qy5\nfJQPctUXyXSt6FiL0+SOq9asP2vaF+2DUviANn1lp7IWIzUKA815/tpodhmlM2vm\nNEdpj+CEa3K0Gpoh0qfXkQKBgQCCwOB6APfVjeFbX8wwAZIRgp3cY1i5KuFX9KDb\nW1WsFy1tGWa27ymtaad3Hj1D/UrGFqtRe4u10so/eeOYPYL2cfStljbAbEUL0Dbh\n4j0jDVx3DTclJNyr2VDhPc4EfOUhzHp5uaeOiJXmMwOwpRXWMTC6B+8jzB4G3aQ+\nt8TnQQKBgQDCLjDCEc/l3KHQYfTpxX1EIvoqEJSIRUyXjuICj0kP+fBXcWiYEEd4\njJTryVRmIulyJTuxAhhBNXlHGIMPX2fmU7IGgRKO/2kvb2yLGTnfecUGwPL4YEGy\nw0yCPjyhu9/fpr1lDUJ0NN+GmpqplkqvXtYPLdJSIigDVW7Jn/stRQ==\n-----END RSA PRIVATE KEY-----"
    g_public_key_pem = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1ZTVl1y9Zh2ZJ0EOW8eo\n+2EFBBRiHoDJazdLO+dckpHDpwwQLmwKquZqVhCogUQmIHJZ6b6QlFcxX0fTvizF\n0SsocvKeJ5orgaMeC2kjkgf1gMecwRDkn7tFhoezQ8xYGhlcZVho9CzBJKNmmDoh\nqkWpgguAOQnEzt07c2o5drH03km9nF1Nbsu/B05CozK3LRC+mnZUowNwtzQV7tPA\nYLshpK+awmJ8upqAwy+7JHXPfVz/beShMuMXxGi28jUYe5rGLWrO73xbkxMkI+dK\n0Gxym0UG1LodR9hp+EmWoem8HJqYE5L1HhqJCy8bNP+5EeXFhaohRfMhMcWE9AIn\nswIDAQAB\n-----END PUBLIC KEY-----"
    
    key_pair = {
        "_id": polling_place_id,
        "polling_place_id": polling_place_id,
        "private_key_pem": private_key_pem,
        "public_key_pem": public_key_pem,
        "g_private_key_pem": g_private_key_pem,
        "g_public_key_pem": g_public_key_pem
    }
    await DB.key_pairs.insert_one(key_pair)


print("Seeding key pairs...")
asyncio.run(seed())
print("Seeding key pairs... Done!")
