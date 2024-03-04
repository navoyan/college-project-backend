from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .exceptions import InvalidAccessToken
from .schemas import TokenData
from src.config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="tokens")


async def get_current_token(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_signing_secret_key,
            algorithms=[settings.jwt_signing_algorithm],
        )

        return TokenData(
            email=payload.get("email"),
            full_name=payload.get("full_name"),
        )
    except JWTError:
        raise InvalidAccessToken
