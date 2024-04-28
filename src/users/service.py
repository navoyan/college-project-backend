import secrets
import string

from fastapi_mail import MessageSchema, MessageType
from passlib.context import CryptContext

from src import mongo, redis, mail
from .exceptions import EmailAlreadyExists, InvalidOrExpiredValidationToken
from .schemas import (
    User,
    UserDetails,
    PersistedUser,
    UserRole,
    UserCreationRequest,
    EmailValidationTemplateBody,
)

crypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_USER_CREATION_REQUEST_TTL = 60 * 60


async def find_user(email: str) -> User | None:
    user_dict = await mongo.users_collection.find_one({"email": email})
    if user_dict:
        return User(**user_dict)
    else:
        return None


async def request_user_creation(details: UserDetails):
    user = await find_user(details.email)
    if user:
        raise EmailAlreadyExists

    validation_token = generate_email_validation_token()
    redis_key = f"user_creation_request:{validation_token}"

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
        hashed_password=crypt_context.hash(details.password),
    )

    await redis.client.set(
        redis_key, user_creation_request.model_dump_json(), ex=_USER_CREATION_REQUEST_TTL, nx=True
    )


async def proceed_user_creation(validation_token: str):
    redis_key = f"user_creation_request:{validation_token}"
    user_creation_request_json = await redis.client.get(redis_key)
    if not user_creation_request_json:
        raise InvalidOrExpiredValidationToken

    user_creation_request = UserCreationRequest.model_validate_json(user_creation_request_json)
    await create_user_using_request(user_creation_request, role=UserRole.user)

    await redis.client.delete(redis_key)


async def create_user_using_details(details: UserDetails, role: UserRole = UserRole.user) -> User:
    if await find_user(details.email):
        raise EmailAlreadyExists

    user = PersistedUser(
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
