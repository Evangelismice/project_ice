from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class GalleryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    caption: Optional[str] = None
    url: str
    created_at: Optional[datetime] = None
