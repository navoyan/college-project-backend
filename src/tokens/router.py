from typing import Annotated

from fastapi import APIRouter, Depends

from src.tokens import service as token_service
from src.tokens.schemas import TokenResponse
from src.users.dependencies import get_current_user_using_credentials
from src.users.schemas import User

router = APIRouter(prefix="/tokens", tags=["Tokens"])


@router.post("/")
def create_access_token(
    user: Annotated[User, Depends(get_current_user_using_credentials)]
) -> TokenResponse:
    access_token = token_service.create_access_token(user)

    return TokenResponse(access_token=access_token)
