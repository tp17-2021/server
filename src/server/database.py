import os
import motor.motor_asyncio

CLIENT = motor.motor_asyncio.AsyncIOMotorClient(
    f"{os.environ['SERVER_DB_HOST']}:{os.environ['SERVER_DB_PORT']}"
)
DB = CLIENT[os.environ["SERVER_DB_NAME"]]

