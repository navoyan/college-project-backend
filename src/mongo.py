from typing import Any
from contextlib import asynccontextmanager

from motor.core import AgnosticClient, AgnosticCollection, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings


users_collection: AgnosticCollection[dict[str, Any]]


@asynccontextmanager
async def lifespan(_):
    global users_collection

    mongo_client: AgnosticClient[dict[str, Any]] = AsyncIOMotorClient(
        host=settings.mongo_host,
        username=settings.mongo_username,
        password=settings.mongo_password,
    )

    database: AgnosticDatabase[dict[str, Any]] = mongo_client[settings.mongo_database]
    await database.command("ping")

    users_collection: AgnosticCollection[dict[str, Any]]  = database["users"]

    yield

    mongo_client.close()

