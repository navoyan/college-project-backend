from enum import Enum

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class User(BaseModel):
    full_name: str
    email: str
    role: UserRole = UserRole.user


class PersistedUser(User):
    hashed_password: str


class UserCredentials(BaseModel):
    email: str
    password: str


class UserDetails(UserCredentials):
    full_name: str


class UserCreationRequest(BaseModel):
    email: EmailStr
    full_name: str
    hashed_password: str


class EmailValidationTemplateBody(BaseModel):
    full_name: str
    validation_token: str
