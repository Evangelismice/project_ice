from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from .base import Base
from ..enums import MemberType


class Member(Base):
    __tablename__ = 'members'

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String(150), nullable=False, index=True)
    member_type = Column(Enum(MemberType), nullable=False, default=MemberType.member)
    phone = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
