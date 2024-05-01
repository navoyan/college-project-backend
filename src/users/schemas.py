from enum import Enum

from pydantic import BaseModel, EmailStr, Field

from src.mongo import ModelObjectId


class UserRole(str, Enum):
    admin = "admin"
    user = "user"


class User(BaseModel):
    id: ModelObjectId = Field(alias="_id")
    full_name: str
    email: str
    role: UserRole = UserRole.user


class PersistedUser(User):
    points: int = 0
    hashed_password: str


class UserCredentials(BaseModel):
    email: str
    password: str


class UserDetails(UserCredentials):
    full_name: str


class UserResponse(User):
    points: int


class UserCreationRequest(BaseModel):
    email: EmailStr
    full_name: str
    validation_token: str
    hashed_password: str


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    password: str | None = None


class EmailValidationTemplateBody(BaseModel):
    full_name: str
    validation_token: str
