from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.collection import Collection

from .config import settings


users_collection: Collection


@asynccontextmanager
async def lifespan(_):
    global users_collection

    mongo_client = AsyncIOMotorClient(
        host=settings.mongo_host,
        username=settings.mongo_username,
        password=settings.mongo_password,
    )

    database = mongo_client.get_database(settings.mongo_database)
    await database.command("ping")

    users_collection = database.get_collection("users")

    yield

    mongo_client.close()
    users_collection = None
