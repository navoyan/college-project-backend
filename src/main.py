from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import mongo, redis, init_setups

from .tokens.router import router as tokens_router
from .users.router import router as users_router


@asynccontextmanager
async def app_lifespan(ctx: FastAPI):
    lifespans = [
        mongo.lifespan(ctx),
        redis.lifespan(ctx),
        init_setups.lifespan(ctx),
    ]

    for lifespan in lifespans:
        await lifespan.__aenter__()

    yield

    for lifespan in lifespans:
        await lifespan.__aexit__(None, None, None)


app = FastAPI(lifespan=app_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tokens_router)
app.include_router(users_router)
