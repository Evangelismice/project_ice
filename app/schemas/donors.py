from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from ..enums import DonorType


class DonorBase(BaseModel):
    name: str
    donor_type: DonorType = DonorType.individual
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class DonorCreate(DonorBase):
    pass


class DonorUpdate(BaseModel):
    name: Optional[str] = None
    donor_type: Optional[DonorType] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class DonorResponse(DonorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
