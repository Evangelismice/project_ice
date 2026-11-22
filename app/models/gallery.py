from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base


class GalleryImage(Base):
    __tablename__ = 'gallery_images'

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    resource_type = Column(String(20), nullable=False, default='image')  # image or video
    image_url = Column(String(500), nullable=True)
    video_url = Column(String(500), nullable=True)
    description = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())