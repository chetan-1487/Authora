# schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID as uuid

class UserResponse(BaseModel):
    id: uuid
    name: str
    email: EmailStr
    is_verified: bool

    class Config:
        from_attributes = True

class UpdateUserRequest(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginSuccessResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"