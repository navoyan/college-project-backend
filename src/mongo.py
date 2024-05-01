from typing import Any
from contextlib import asynccontextmanager

from motor.core import AgnosticClient, AgnosticCollection, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings


users_collection: AgnosticCollection
user_creation_requests_collection: AgnosticCollection

@asynccontextmanager
async def lifespan(_):
    global users_collection
    global user_creation_requests_collection

    mongo_client: AgnosticClient = AsyncIOMotorClient(
        host=settings.mongo_host,
        username=settings.mongo_username,
        password=settings.mongo_password,
    )

    database: AgnosticDatabase = mongo_client[settings.mongo_database]
    await database.command("ping")

    users_collection = database.get_collection("users")
    user_creation_requests_collection = database["user_creation_requests"]

    yield

    mongo_client.close()
