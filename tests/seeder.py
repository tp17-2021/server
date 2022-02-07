import random
import json
import string
import os
import motor.motor_asyncio
import asyncio


async def get_parties_with_candidates(DB):
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


async def load_json(path):
    """
    Helper to load json file
    """
    with open(path, encoding="utf8") as file:
        return json.load(file)


async def seed():
    CLIENT = motor.motor_asyncio.AsyncIOMotorClient(
        f"{os.environ['SERVER_DB_HOST']}:{os.environ['SERVER_DB_PORT']}"
    )
    DB = CLIENT[os.environ["SERVER_DB_NAME"]]

    random.seed(1)

    DB.parties.drop()
    DB.candidates.drop()
    DB.polling_places.drop()
    DB.votes.drop()
    DB.key_pairs.drop()

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
            "candidates_ids": [],
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
            vote["candidates_ids"].append(selected_candidate["_id"])

        votes_to_be_inserted.append(vote)

    await DB.votes.insert_many(votes_to_be_inserted)

    # key pair for polling_place_id = 0
    polling_place_id = 0

    aes_key = "LSH63IWHrJmm7VkLt+eTX35ON5jYqtYBf3hDeC4ZYkU="
    private_key_pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEAs6lvNfr+Eo6Mt+mW95fhjUbCRygCNok8Y8yIu502lpDiz3bN\ndR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7IEpRSmY1nElabMoBbU2vsPWBsu7WR\n31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPuRVtuHy/q2tD5sY2ekWJc1YsoeQ5J\nDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c2P4NpNgSJ2NT8aF/bDbu3sQk9QuQ\nXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchqrYj5Xnql/wcrnyOhcgeKsOBieH/f\nETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG47QIDAQABAoIBAAEotU5QfGpm8gUF\n/64cOMs1Bm/4E+QmCFrF5IQ1VFvlBBmQGZGko6i6AHR0CtCN2OuVAne9sTtfYyjU\nLvPdzUcMQ3q40+B3n5BB6UvFZ2SIiu1RE3nDCRyFx/VWATEqwZKTmaEUsO1BMHwx\nJWW5+K4tb1HunUZ20M2OEfkps39438Vk1R4I/kJqhp8E7mLYshBHyK1OwOgiInE4\n1Z2SwAhvGKnNE3TnBlV7/K5XFQg3b7QWORHvlvnNHU7ed8TXmizp7No6Qxl1ZJ2z\nier3f+XiMAryIb7AyBJyIWGnQllrDhff5hhNObltLmmaAkQm3LSsJ52GU9e4i/6c\nF/sshLECgYEAu78IM4Sj3D+wd6lMNVInU7Np8o8L5Ihq9Y1ccHmyvbVdxeGPIfKo\n/j/WwoCQJPKFQJLjQru3s1nVOOYNE5/CUQEEeFguzRL43UtzywONc1+L4a2MOnqO\n8ywQF1OrxByFy9eFLdN5ETdDhriajx8VM0hRrmeLsiGcmVZet1lFjjkCgYEA9PoD\n3x2qaCrTe3mZPHzfayHYWVFFxvRYOjxmIbOdzQZPeQA1tXEHyHnY/z3ibA+v3iQu\nQ2n5RQM4/+ItjS2xrwL+hlU3yue67HfBuUyFcFjhEUu0sdN4439d3K9hAeX7eTfB\nZ2CsNieqPxYZj6tSL4+0Fru4o4VpD79u7pSlgFUCgYAdWiJoG4aauoJWUuuNMojf\ndx9LQr3zPriqJy2akAw3yJEejMMZ5ZwyE7z5r6vZeukGTXCmUD7KFXNWb/D/bmys\nyWHvhqnaeerafh9eT/HfZcKyx7Uyt1J+BheF7hjeki8AzXMO1Q8Kd/9gop/XXF6u\nI9JRV/LpKIQZHP214IkVUQKBgQCpqO09fIIkGmTUwuZJagIhZBM96Hd2zoq76lCh\nTpAfChvIJUkNG/bT9O8/9k/1nveh1VTlA2PLU+wJ606408iW+G/mAObe85YVZusX\ntdNEd4mIPPIrpdW3WOJckGmSswBydxbOzbj22Imjn16cjX4hylhi1ieNuDuG2IGv\nYess8QKBgQCrT1ATnUxqacw/x8RRJpZWV4rnrkujA2XPLu4YaMODzVSkk+HVEabH\nJtA4AV6O0bneAgywBltg9wL0L98Q6ckuEo6hA9rskvwxQAk9uawJDzy1Bq/aEcSD\nu707LpYyMboRA/+1Sw8GEYF1iKdVJnGN1pjse4V4mJvobPPEZ+4Atw==\n-----END RSA PRIVATE KEY-----"
    public_key_pem = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAs6lvNfr+Eo6Mt+mW95fh\njUbCRygCNok8Y8yIu502lpDiz3bNdR5qRZndlq7k+8XmIv2Qm8yD9BeBJbSyvc7I\nEpRSmY1nElabMoBbU2vsPWBsu7WR31pGDtAnQYCOvofScT98lar5WY5EOIV7ZzPu\nRVtuHy/q2tD5sY2ekWJc1YsoeQ5JDK64qXHZsGaIjblm+gQemucv5TG80+sgzf7c\n2P4NpNgSJ2NT8aF/bDbu3sQk9QuQXTEnkgFxTPWCwhYzRvsyq6dSTnlbyk8xfchq\nrYj5Xnql/wcrnyOhcgeKsOBieH/fETheNm6xC6Ol9Zo0rFdtqgBDsIN6H5aPCfG4\n7QIDAQAB\n-----END PUBLIC KEY-----"

    key_pair = {
        "_id": 0,
        "polling_place_id": polling_place_id,
        "aes_key": aes_key,
        "private_key_pem": private_key_pem,
        "public_key_pem": public_key_pem
    }
    await DB.key_pairs.insert_one(key_pair)

asyncio.run(seed())
