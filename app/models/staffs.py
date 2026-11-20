from sqlalchemy import Column, Integer, String, Date, DateTime, Enum
from sqlalchemy.sql import func
from .base import Base
from ..enums import Gender, Department, StaffStatus


class Staff(Base):
    __tablename__ = 'staffs'

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    gender = Column(Enum(Gender), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(30), nullable=True)
    address = Column(String(255), nullable=True)
    department = Column(Enum(Department), nullable=False)
    position = Column(String(100), nullable=True)
    date_joined = Column(Date, nullable=True)
    status = Column(Enum(StaffStatus), nullable=False, default=StaffStatus.active)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
