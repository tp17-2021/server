import os
import pymongo

CLIENT = None
DB = None

def init():
    global CLIENT, DB
        
    try:
        timeout = 5
        MONGO_URI = f'{os.environ["SERVER_DB_HOST"]}:{os.environ["SERVER_DB_PORT"]}'
        CLIENT = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=timeout)
        CLIENT.server_info()

        DB = CLIENT[os.environ["SERVER_DB_NAME"]]

        # return DB, CLIENT

        # if os.environ["SERVER_DB_NAME"] in CLIENT.list_database_names():
        #     DB = CLIENT[os.environ["SERVER_DB_NAME"]]
        # else:
        #     raise Exception(f'{os.environ["SERVER_DB_NAME"]} does not exist')

    except pymongo.errors.ServerSelectionTimeoutError as err:
        raise err

init()