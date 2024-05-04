from typing import Annotated, Any
from contextlib import asynccontextmanager

from bson import ObjectId
from fastapi import Depends, HTTPException, Path
from motor.core import AgnosticClient, AgnosticCollection, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import (
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

from .config import settings


users_collection: AgnosticCollection
user_creation_requests_collection: AgnosticCollection
quizes_collection: AgnosticCollection


@asynccontextmanager
async def lifespan(_):
    global users_collection
    global user_creation_requests_collection
    global quizes_collection

    mongo_client: AgnosticClient = AsyncIOMotorClient(
        host=settings.mongo_host,
        username=settings.mongo_username,
        password=settings.mongo_password,
    )

    database: AgnosticDatabase = mongo_client[settings.mongo_database]
    await database.command("ping")

    users_collection = database.get_collection("users")
    user_creation_requests_collection = database.get_collection("user_creation_requests")
    quizes_collection = database.get_collection("quizes")

    yield

    mongo_client.close()


class ObjectIdAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        *_,
    ):
        def validate_from_str(value: str) -> ObjectId:
            return ObjectId(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


ModelObjectId = Annotated[ObjectId, ObjectIdAnnotation]


def path_param_object_id(id: Annotated[str, Path()]) -> ObjectId:
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(
            status_code=400, detail="Provided path parameter is invalid BSON ObjectId"
        )
