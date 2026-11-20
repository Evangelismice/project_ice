from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from ..enums import DonorType


class Donor(Base):
    __tablename__ = 'donors'

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    donor_type = Column(Enum(DonorType), nullable=False, default=DonorType.individual)
    email = Column(String(255), nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    donations = relationship('Donation', back_populates='donor', cascade='all, delete-orphan')
