from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    subject: Optional[str] = Field(default=None, max_length=150)
    message: str = Field(min_length=5, max_length=5000)
    website: Optional[str] = None  # honeypot field: real visitors leave it empty


class ContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    subject: Optional[str] = None
    message: str
    is_read: bool
    created_at: Optional[datetime] = None
