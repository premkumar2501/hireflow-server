from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str
    username: str
    phoneNo: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: str = None
    username: str = None
    phoneNo: str = None
    password: str | None = None


class UserResponse(UserBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class RegisterResponse(BaseModel):
    user: UserResponse
    verification_token: str


class VerifyUser(BaseModel):
    id: int
    token: str


class LoginRequest(BaseModel):
    email: str
    password: str
    