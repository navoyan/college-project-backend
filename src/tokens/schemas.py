from pydantic import BaseModel, EmailStr

from src.mongo import ModelObjectId
from src.users.schemas import UserRole


class TokenData(BaseModel):
    id: ModelObjectId 
    email: str
    full_name: str
    role: UserRole


class TokenResponse(BaseModel):
    access_token: str
