from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from ..enums import Gender, Department, StaffStatus


class StaffBase(BaseModel):
    first_name: str
    last_name: str
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    department: Department
    position: Optional[str] = None
    date_joined: Optional[date] = None
    status: StaffStatus = StaffStatus.active


class StaffCreate(StaffBase):
    pass


class StaffUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[Gender] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    department: Optional[Department] = None
    position: Optional[str] = None
    date_joined: Optional[date] = None
    status: Optional[StaffStatus] = None


class StaffResponse(StaffBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
