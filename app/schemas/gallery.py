from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class GalleryCreate(BaseModel):
    resource_type: str = Field(default='image', pattern='^(image|video)$')
    image_url: Optional[str] = Field(default=None, max_length=500)
    video_url: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=150)


class GalleryUpdate(BaseModel):
    resource_type: Optional[str] = Field(default=None, pattern='^(image|video)$')
    image_url: Optional[str] = Field(default=None, max_length=500)
    video_url: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=150)


class GalleryResponse(GalleryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None