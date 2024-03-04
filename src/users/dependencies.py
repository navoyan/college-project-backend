from typing import Annotated

from fastapi import Depends

from src import mongo
from src.users import service as users_service
from src.tokens.dependencies import get_current_token
from src.tokens.schemas import TokenData
from .exceptions import IncorrectCredentials
from .schemas import User, UserCredentials


def get_current_user_using_credentials(credentials: UserCredentials) -> User:
    user = mongo.users_collection.find_one({"email": credentials.email})

    if not user or not users_service.verify_password(
            credentials.password, user.hashed_password
    ):
        raise IncorrectCredentials

    return user


def get_current_user_using_token(
    token_data: Annotated[TokenData, Depends(get_current_token)]
) -> User:
    return User(
        email=token_data.email,
        full_name=token_data.full_name,
        role=token_data.role,
    )
