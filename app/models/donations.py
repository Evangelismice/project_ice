from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, Foreignkey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from ..enums import PaymentMethod


class Donation(Base):
    __tablename__ = 'donations'

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    donor_id = Column(Integer, ForeignKey('donors.id'), nullable=False, index=True)
    amount = Column(Numeric(14, 2), nullable=False)
    currency = Column(String(10), nullable=False, default='NGN')
    purpose = Column(String(255), nullable=True)
    payment_method = Column(Enum(PaymentMethod), nullable=False, default=PaymentMethod.cash)
    date_received = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    receipt = Column(String(255), nullable=True)  # path to receipt image

    donor = relationship('Donor', back_populates='donations')
