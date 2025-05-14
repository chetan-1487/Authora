from pydantic import BaseModel, EmailStr, constr, field_validator, ValidationError
from fastapi import UploadFile, File
import re

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=8)
    profile_picture: UploadFile = File(...)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[@$!%*?&]', password):
            raise ValueError("Password must contain at least one special character (@$!%*?&)")
        return password

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: constr(min_length=8)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, new_password: str):
        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', new_password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', new_password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r'\d', new_password):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r'[@$!%*?&]', new_password):
            raise ValueError("Password must contain at least one special character (@$!%*?&)")
        return new_password
