from contextlib import asynccontextmanager

from redis.asyncio import Redis
from src.config import settings

client: Redis


@asynccontextmanager
async def lifespan(_):
    global client

    client = Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        username=settings.redis_username,
        password=settings.redis_password,
    )
    await client.ping()

    yield

    await client.aclose()
