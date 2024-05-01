from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi import status
from fastapi.responses import Response, RedirectResponse
from starlette.status import HTTP_202_ACCEPTED

from src.users import service as users_service
from src.users.dependencies import get_current_user
from src.users.schemas import User, UserDetails

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/creation-requests")
async def request_user_creation(details: UserDetails) -> Response:
    await users_service.request_user_creation(details)

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post("/")
async def create_user(validation_token: Annotated[str, Form()]) -> Response:
    await users_service.proceed_user_creation(validation_token)

    return Response(status_code=HTTP_202_ACCEPTED)


@router.get("/me")
async def get_current_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    return current_user
