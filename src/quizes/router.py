from typing import Annotated
from bson.objectid import ObjectId
from fastapi import APIRouter, Depends, status
from starlette.status import HTTP_200_OK

from src.mongo import path_param_object_id
from src.users.schemas import User

from .schemas import (
    Quiz,
    QuizAdminResponse,
    QuizCreationRequest,
    QuizResponse,
    QuizUpdateRequest,
    VerifyCompletionRequest,
)
from src.quizes import service as quizes_service
from src.users.dependencies import get_current_user, get_required_admin_user


router = APIRouter(prefix="/quizes", tags=["Quizes"])


@router.get("/", status_code=HTTP_200_OK)
async def fetch_all_quizes(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[QuizResponse | QuizAdminResponse]:
    return await quizes_service.find_all_quizes(current_user)


@router.get("/{id}", status_code=HTTP_200_OK)
async def find_quiz(
    current_user: Annotated[User, Depends(get_current_user)],
    id: Annotated[ObjectId, Depends(path_param_object_id)],
) -> QuizResponse | QuizAdminResponse:
    return await quizes_service.find_quiz_by_id(current_user, id)


@router.post(
    "/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_required_admin_user)]
)
async def create_quiz(create_request: QuizCreationRequest) -> Quiz:
    return await quizes_service.create_quiz(create_request)


@router.patch("/{id}", status_code=HTTP_200_OK, dependencies=[Depends(get_required_admin_user)])
async def update_quiz(
    id: Annotated[ObjectId, Depends(path_param_object_id)], update: QuizUpdateRequest
) -> Quiz:
    return await quizes_service.update_quiz_by_id(id, update)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_required_admin_user)]
)
async def delete_quiz(id: Annotated[ObjectId, Depends(path_param_object_id)]):
    return await quizes_service.delete_quiz_by_id(id)


@router.post("/{id}/verified-completion", status_code=HTTP_200_OK)
async def verify_quiz_completion(
    id: Annotated[ObjectId, Depends(path_param_object_id)],
    current_user: Annotated[User, Depends(get_current_user)],
    verified_completion: VerifyCompletionRequest,
):
    await quizes_service.verify_quiz_completion(id, current_user, verified_completion)
