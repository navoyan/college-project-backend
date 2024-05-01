from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, Depends, Form
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_202_ACCEPTED, HTTP_204_NO_CONTENT

from src.mongo import path_param_object_id
from src.users import service as users_service
from src.users.dependencies import get_current_user, get_required_admin_user
from src.users.schemas import User, UserDetails, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/creation-requests", status_code=HTTP_202_ACCEPTED)
async def request_user_creation(details: UserDetails):
    await users_service.request_user_creation(details)


@router.post("/", status_code=HTTP_201_CREATED)
async def create_user(validation_token: Annotated[str, Form()]) -> User:
    return await users_service.proceed_user_creation(validation_token)


@router.get("/me", status_code=HTTP_200_OK)
async def current_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.get("/", status_code=HTTP_200_OK, dependencies=[Depends(get_required_admin_user)])
async def find_all_users() -> list[User]:
    return await users_service.find_all_users()


@router.get("/{id}", status_code=HTTP_200_OK, dependencies=[Depends(get_required_admin_user)])
async def find_user_by_id(id: Annotated[ObjectId, Depends(path_param_object_id)]) -> User:
    return await users_service.find_user_by_id(id)


@router.patch("/me", status_code=HTTP_200_OK)
async def update_current_user(
    current_user: Annotated[User, Depends(get_current_user)], update: UserUpdateRequest
) -> User:
    return await users_service.update_user_by_id(current_user.id, update)


@router.patch("/{id}", status_code=HTTP_200_OK, dependencies=[Depends(get_required_admin_user)])
async def update_user_by_id(
    id: Annotated[ObjectId, Depends(path_param_object_id)], update: UserUpdateRequest
) -> User:
    return await users_service.update_user_by_id(id, update)


@router.delete("/me", status_code=HTTP_204_NO_CONTENT)
async def delete_current_user(current_user: Annotated[User, Depends(get_current_user)]):
    return await users_service.delete_user_by_id(current_user.id)


@router.delete(
    "/{id}", status_code=HTTP_204_NO_CONTENT, dependencies=[Depends(get_required_admin_user)]
)
async def delete_user_by_id(id: Annotated[ObjectId, Depends(path_param_object_id)]):
    return await users_service.delete_user_by_id(id)
