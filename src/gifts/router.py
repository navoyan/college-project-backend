from typing import Annotated
from bson.objectid import ObjectId
from fastapi import APIRouter, Body, Depends, Response, status
from starlette.status import HTTP_200_OK

from src.gifts.schemas import (
    Gift,
    GiftAdminResponse,
    GiftCreationRequest,
    GiftResponse,
    GiftUpdateRequest,
    VerifyReceiptRequest,
    VerifyReceiptResponse,
)
from src.mongo import path_param_object_id

from src.gifts import service as gifts_service
from src.users.dependencies import get_current_user, get_required_admin_user
from src.users.schemas import User


router = APIRouter(prefix="/gifts", tags=["Gifts"])


@router.get("/", status_code=HTTP_200_OK)
async def fetch_all_gifts(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[GiftResponse | GiftAdminResponse]:
    return await gifts_service.find_all_gifts(current_user)


@router.get("/{id}", status_code=HTTP_200_OK)
async def find_gift(
    id: Annotated[ObjectId, Depends(path_param_object_id)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> GiftResponse | GiftAdminResponse:
    return await gifts_service.find_gift_by_id(current_user, id)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_required_admin_user)],
)
async def create_gift(create_request: GiftCreationRequest) -> Gift:
    return await gifts_service.create_gift(create_request)


@router.patch(
    "/{id}",
    status_code=HTTP_200_OK,
    dependencies=[Depends(get_required_admin_user)],
)
async def update_gift(
    id: Annotated[ObjectId, Depends(path_param_object_id)], update: GiftUpdateRequest
) -> Gift:
    return await gifts_service.update_gift_by_id(id, update)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_required_admin_user)],
)
async def delete_gift(id: Annotated[ObjectId, Depends(path_param_object_id)]):
    await gifts_service.delete_gift_by_id(id)


@router.post(
    "/{id}/verified-receival",
    status_code=HTTP_200_OK,
    dependencies=[Depends(get_required_admin_user)],
)
async def verify_quiz_completion(
    id: Annotated[ObjectId, Depends(path_param_object_id)],
    verify_receipt: VerifyReceiptRequest,
) -> VerifyReceiptResponse:
    return await gifts_service.verify_gift_receipt(id, verify_receipt)


@router.put(
    "/{id}/image",
    status_code=HTTP_200_OK,
    dependencies=[Depends(get_required_admin_user)],
)
async def upload_gift_image(
    id: Annotated[ObjectId, Depends(path_param_object_id)],
    gift_image_binary: Annotated[bytes, Body(media_type="image/*")],
):
    await gifts_service.upload_gift_image(id, gift_image_binary)


@router.get(
    "/{id}/image",
    status_code=HTTP_200_OK,
    dependencies=[Depends(get_required_admin_user)],
)
async def fetch_gift_image(
    id: Annotated[ObjectId, Depends(path_param_object_id)],
) -> Response:
    image_binary = await gifts_service.fetch_gift_image(id)

    return Response(
        content=image_binary,
        media_type="image/*",
    )
