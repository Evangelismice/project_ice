from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class Registration(Base):
    __tablename__ = 'registrations'

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    event_id = Column(Integer, ForeignKey('events.id'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(30), nullable=True)
    church = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    event = relationship('Event', back_populates='registrations')

    @property
    def event_title(self):
        return self.event.title if self.event else None
