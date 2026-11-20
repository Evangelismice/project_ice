from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegistrationCreate(BaseModel):
    event_id: int
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=30)
    church: Optional[str] = Field(default=None, max_length=150)
    website: Optional[str] = None  # honeypot


class RegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    event_title: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    church: Optional[str] = None
    created_at: Optional[datetime] = None
