from pydantic import BaseModel, Field

from src.mongo import ModelObjectId


class VerifiedReceipt(BaseModel):
    receiver_id: ModelObjectId
    receipt_timestamp: float


class Gift(BaseModel):
    id: ModelObjectId = Field(alias="_id")
    name: str
    price_points: int
    category: str
    verified_receipts: list[VerifiedReceipt] = []


class GiftCreationRequest(BaseModel):
    name: str
    price_points: int
    category: str


class GiftUpdateRequest(BaseModel):
    name: str | None = None
    price_points: int | None = None
    category: str | None = None


class GiftResponse(BaseModel):
    id: ModelObjectId = Field(alias="_id")
    name: str
    price_points: int
    category: str
    verified_receipt: bool


class GiftAdminResponse(BaseModel):
    id: ModelObjectId = Field(alias="_id")
    name: str
    price_points: int
    category: str
    verified_receipts: list[VerifiedReceipt] = []


class VerifyReceiptRequest(BaseModel):
    receiver_id: ModelObjectId


class VerifyReceiptResponse(BaseModel):
    receiver_id: ModelObjectId
    receipt_timestamp: float
