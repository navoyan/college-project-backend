import time
from bson.objectid import ObjectId
from pymongo import ReturnDocument
from src import gifts, mongo
from src.gifts.exceptions import GiftAlreadyReceived, GiftNotFound, NotEnoughPoints
from src.gifts.schemas import (
    Gift,
    GiftAdminResponse,
    GiftCreationRequest,
    GiftResponse,
    GiftUpdateRequest,
    VerifiedReceipt,
    VerifyReceiptRequest,
    VerifyReceiptResponse,
)
from src.users.exceptions import UserNotFound
from src.users.schemas import PersistedUser, User, UserRole


async def find_all_gifts(current_user: User) -> list[GiftResponse | GiftAdminResponse]:
    gift_dicts = await mongo.gifts_collection.find({}).to_list(None)

    return list(map(lambda gift_dict: _build_gift_response(current_user, gift_dict), gift_dicts))


async def find_gift_by_id(current_user: User, id: ObjectId) -> GiftResponse | GiftAdminResponse:
    gift_dict = await mongo.gifts_collection.find_one({"_id": id})

    if gift_dict is None:
        raise GiftNotFound

    return _build_gift_response(current_user, gift_dict)


def _build_gift_response(current_user: User, gift_dict: dict) -> GiftResponse | GiftAdminResponse:
    if current_user.role == UserRole.admin:
        return GiftAdminResponse(**gift_dict)
    else:
        gift = Gift(**gift_dict)
        verified_receipt = any(
            current_user.id == receipt.user_id for receipt in gift.verified_receipts
        )
        return GiftResponse(verified_receipt=verified_receipt, **gift_dict)


async def create_gift(creation_request: GiftCreationRequest) -> Gift:
    creation_request_dict = creation_request.model_dump()
    insert_result = await mongo.gifts_collection.insert_one(creation_request_dict)

    creation_request_dict["_id"] = insert_result.inserted_id
    return Gift(**creation_request_dict)


async def upload_gift_image(id: ObjectId, gift_image_binary: bytes):
    await mongo.gifts_collection.update_one({"_id": id}, {"$set": {"image": gift_image_binary}})


async def fetch_gift_image(id: ObjectId) -> bytes:
    gift_dict = await mongo.gifts_collection.find_one({"_id": id}, {"image": True})

    if gift_dict is None:
        raise GiftNotFound

    return gift_dict["image"]


async def update_gift_by_id(id: ObjectId, update: GiftUpdateRequest) -> Gift:
    update_dict = update.model_dump(exclude_unset=True)

    updated_gift_dict = await mongo.gifts_collection.find_one_and_update(
        {"_id": id}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
    )

    if updated_gift_dict is None:
        raise GiftNotFound

    return Gift(**updated_gift_dict)


async def delete_gift_by_id(id: ObjectId):
    delete_result = await mongo.gifts_collection.delete_one({"_id": id})

    if delete_result.deleted_count == 0:
        raise GiftNotFound


async def verify_gift_receipt(
    gift_id: ObjectId, verify_receipt: VerifyReceiptRequest
) -> VerifyReceiptResponse:
    receiver_id = verify_receipt.receiver_id

    gift_dict = await mongo.gifts_collection.find_one({"_id": gift_id})
    if gift_dict is None:
        raise GiftNotFound
    gift = Gift(**gift_dict)

    if any(receiver_id == receipt.receiver_id for receipt in gift.verified_receipts):
        raise GiftAlreadyReceived

    user_dict = await mongo.users_collection.find_one({"_id": receiver_id})
    if user_dict is None:
        raise UserNotFound
    user = PersistedUser(**user_dict)

    if user.points < gift.price_points:
        raise NotEnoughPoints

    receipt = VerifiedReceipt(
        receiver_id=receiver_id,
        receipt_timestamp=time.time(),
    )
    receipt_dict = receipt.model_dump()

    await mongo.users_collection.update_one(
        {"_id": user.id}, {"$inc": {"points": -gift.price_points}}
    )

    await mongo.gifts_collection.update_one(
        {"_id": gift_id}, {"$push": {"verified_receipts": receipt_dict}}
    )

    return VerifyReceiptResponse(**receipt_dict)
