from pydantic import BaseModel, EmailStr, constr
from fastapi import UploadFile, File


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: constr(min_length=8)
    profile_picture: UploadFile = File(...)


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
