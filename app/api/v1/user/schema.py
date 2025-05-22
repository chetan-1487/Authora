# schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID as uuid
from fastapi import UploadFile


class UserResponse(BaseModel):
    id: uuid
    name: str
    email: EmailStr
    profile_picture: Optional[str]
    is_verified: bool

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    name: Optional[str]
    profile_picture: UploadFile = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginSuccessResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
