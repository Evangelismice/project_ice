from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func
from .base import Base


class OnlineGift(Base):
    __tablename__ = 'online_gifts'

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    reference = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(10), nullable=False, default='NGN')
    purpose = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default='pending')
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
