# schema.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_verified: bool

    class Config:
        from_attributes = True

class UpdateUserRequest(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
