from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from ..enums import MemberType


class MemberBase(BaseModel):
    name: str
    member_type: MemberType = MemberType.member
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: Optional[str] = None
    member_type: Optional[MemberType] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class MemberResponse(MemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
