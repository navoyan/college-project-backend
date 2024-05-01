from jose import jwt

from src.config import settings
from src.tokens.schemas import TokenData
from src.users.schemas import User


def create_access_token(user: User) -> str:
    token_data = TokenData(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
    )

    return jwt.encode(
        token_data.model_dump(),
        settings.jwt_signing_secret_key,
        algorithm=settings.jwt_signing_algorithm,
    )
