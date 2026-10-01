from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str
    username: str
    phoneNo: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: str | None = None
    username: str | None = None
    phoneNo: str | None = None
    password: str | None = Field(default=None, min_length=8)


class UserResponse(UserBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

    