import secrets
import string

from fastapi_mail import MessageSchema, MessageType
from passlib.context import CryptContext

from src import mongo, mail
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


async def proceed_user_creation(validation_token: str):
    creation_request_dict = await mongo.user_creation_requests_collection.find_one(
        {"validation_token": validation_token}
    )

    if not creation_request_dict:
        raise InvalidOrExpiredValidationToken

    user_creation_request = UserCreationRequest(**creation_request_dict)
    await create_user_using_request(user_creation_request, role=UserRole.user)

    await mongo.user_creation_requests_collection.delete_one({"validation_token": validation_token})


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
