from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from app.database import Base
from app.utils.enum import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phoneNo = Column(String, unique=True, index=True, nullable=True)
    password = Column(String, nullable=False)
    is_varify = Column(Boolean, default=False)
    role = Column(Enum(UserRole, name="user_role"), nullable=True, server_default=UserRole.CANDIDATE.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=False)