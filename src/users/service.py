import secrets
import string

from bson import ObjectId
from fastapi_mail import MessageSchema, MessageType
from passlib.context import CryptContext
from pymongo import ReturnDocument

from src import mongo, mail
from .exceptions import EmailAlreadyExists, InvalidOrExpiredValidationToken, UserNotFound
from .schemas import (
    User,
    UserDetails,
    PersistedUser,
    UserResponse,
    UserRole,
    UserCreationRequest,
    EmailValidationTemplateBody,
    UserUpdateRequest,
)

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def find_user_by_email(email: str) -> UserResponse | None:
    user_dict = await mongo.users_collection.find_one({"email": email})
    if user_dict:
        return UserResponse(**user_dict)
    else:
        return None


async def find_all_users() -> list[UserResponse]:
    user_dicts = await mongo.users_collection.find({}).to_list(None)

    return list(map(lambda dict: UserResponse(**dict), user_dicts))


async def find_user_by_id(id: ObjectId) -> UserResponse:
    user_dict = await mongo.users_collection.find_one({"_id": id})

    if user_dict:
        return UserResponse(**user_dict)
    else:
        raise UserNotFound


async def update_user_by_id(id: ObjectId, update: UserUpdateRequest) -> UserResponse:
    update_dict = update.model_dump(exclude_unset=True)
    if "password" in update_dict:
        update_dict["hashed_password"] = crypt_context.hash(update_dict.pop("password"))

    updated_user_dict = await mongo.users_collection.find_one_and_update(
        {"_id": id}, {"$set": update_dict}, return_document=ReturnDocument.AFTER
    )

    if updated_user_dict is None:
        raise UserNotFound

    return UserResponse(**updated_user_dict)


async def delete_user_by_id(id: ObjectId):
    delete_result = await mongo.users_collection.delete_one({"_id": id})

    if delete_result.deleted_count == 0:
        raise UserNotFound


async def request_user_creation(details: UserDetails):
    user = await find_user_by_email(details.email)
    if user:
        raise EmailAlreadyExists

    validation_token = generate_email_validation_token()

    email_message_schema = MessageSchema(
        subject="Validate your email on OUR_APP",
        recipients=[details.email],
        subtype=MessageType.html,
        template_body=EmailValidationTemplateBody(
            full_name=details.full_name,
            validation_token=validation_token,
        ).model_dump(),
    )

    await mail.client.send_message(email_message_schema, template_name="email_validation.html")

    user_creation_request = UserCreationRequest(
        email=details.email,
        full_name=details.full_name,
        validation_token=validation_token,
        hashed_password=crypt_context.hash(details.password),
    )

    await mongo.user_creation_requests_collection.insert_one(user_creation_request.model_dump())


async def proceed_user_creation(validation_token: str) -> User:
    creation_request_dict = await mongo.user_creation_requests_collection.find_one(
        {"validation_token": validation_token}
    )

    if not creation_request_dict:
        raise InvalidOrExpiredValidationToken

    user_creation_request = UserCreationRequest(**creation_request_dict)
    user = await create_user_using_request(user_creation_request, role=UserRole.user)

    await mongo.user_creation_requests_collection.delete_one({"validation_token": validation_token})

    return user


async def create_user_using_details(details: UserDetails, role: UserRole = UserRole.user) -> User:
    if await find_user_by_email(details.email):
        raise EmailAlreadyExists

    user = PersistedUser(
        _id=ObjectId(),
        email=details.email,
        full_name=details.full_name,
        role=role,
        hashed_password=crypt_context.hash(details.password),
    )
    await mongo.users_collection.insert_one(user.model_dump())

    return user


async def create_user_using_request(
    request: UserCreationRequest, role: UserRole = UserRole.user
) -> User:
    user = PersistedUser(
        _id=ObjectId(),
        email=request.email,
        full_name=request.full_name,
        role=role,
        hashed_password=request.hashed_password,
    )
    await mongo.users_collection.insert_one(user.model_dump())

    return user


def verify_password(plain_password, hashed_password) -> bool:
    return crypt_context.verify(plain_password, hashed_password)


def generate_email_validation_token() -> str:
    valid_chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(valid_chars) for _ in range(32))
