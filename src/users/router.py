from typing import Annotated

from fastapi import APIRouter, Depends, Form
from fastapi import status
from fastapi.responses import Response, RedirectResponse

from src.users import service as users_service
from src.users.dependencies import get_current_user_using_token
from src.users.schemas import User, UserDetails

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/creation-requests")
async def request_user_creation(details: UserDetails) -> Response:
    await users_service.request_user_creation(details)

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post("/")
async def create_user(validation_token: Annotated[str, Form()]) -> RedirectResponse:
    await users_service.proceed_user_creation(validation_token)

    return RedirectResponse(url="/docs", status_code=status.HTTP_303_SEE_OTHER)  # STUB


@router.get("/me")
async def get_current_user(current_user: Annotated[User, Depends(get_current_user_using_token)]) -> User:
    return current_user
