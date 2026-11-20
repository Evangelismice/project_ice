from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base


class GalleryItem(Base):
    __tablename__ = 'gallery'

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    title = Column(String(150), nullable=False)
    caption = Column(String(255), nullable=True)
    filename = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @property
    def url(self):
        return f'/uploads/{self.filename}'
