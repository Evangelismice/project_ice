from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from ..enums import PaymentMethod


class DonationCreate(BaseModel):
    donor_id: int
    amount: Decimal = Field(gt=0)
    currency: str = 'NGN'
    purpose: Optional[str] = None
    payment_method: PaymentMethod = PaymentMethod.cash
    date_received: date
    receipt: Optional[str] = None


class DonationResponse(DonationCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
