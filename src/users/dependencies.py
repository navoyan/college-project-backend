import logging
from typing import Annotated

from fastapi import Depends, Form

from src import mongo
from src.users import service as users_service
from src.tokens.dependencies import get_current_token
from src.tokens.schemas import TokenData
from .exceptions import IncorrectCredentials, InsufficientUserRights
from .schemas import PersistedUser, User, UserRole


async def get_current_user_using_credentials(
    email: Annotated[str, Form(alias="username")], password: Annotated[str, Form()]
) -> User:
    user_dict = await mongo.users_collection.find_one({"email": email})

    if not user_dict:
        raise IncorrectCredentials

    user = PersistedUser(**user_dict)

    if not users_service.verify_password(password, user.hashed_password):
        raise IncorrectCredentials

    return User(**user_dict)


def get_current_user(token_data: Annotated[TokenData, Depends(get_current_token)]) -> User:
    return User(
        email=token_data.email,
        full_name=token_data.full_name,
        role=token_data.role,
    )
