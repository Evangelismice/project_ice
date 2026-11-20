from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class GiveInitialize(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    amount: Decimal = Field(ge=100, le=100000000)
    purpose: Optional[str] = Field(default=None, max_length=255)


class GiftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    name: str
    email: str
    amount: Decimal
    currency: str
    purpose: Optional[str] = None
    status: str
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
