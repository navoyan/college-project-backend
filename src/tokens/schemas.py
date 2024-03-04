from pydantic import BaseModel, EmailStr

from src.users.schemas import UserRole


class TokenData(BaseModel):
    email: str
    full_name: str
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
