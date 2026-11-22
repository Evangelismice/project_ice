from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GalleryCreate(BaseModel):
    image_url: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=150)


class GalleryUpdate(BaseModel):
    image_url: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=150)


class GalleryResponse(GalleryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None