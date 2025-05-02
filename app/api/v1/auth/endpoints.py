from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from . import schema, service, repository
from ....db.session import get_db
from app.services.email_service import send_otp_email
from fastapi.responses import JSONResponse

router = APIRouter(
    tags=["User Registration"]
)

@router.post("/register")
def register(data: schema.RegisterRequest, db: Session = Depends(get_db)):
    if repository.get_user_by_email(db, data.email):
        raise HTTPException(status_code=200, detail="Email already registered")
    if not service.is_password_strong(data.password):
        raise HTTPException(status_code=400, detail="Weak password")
    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    hashed = service.get_password_hash(data.password)
    user = repository.create_user(db, data.name, data.email, hashed)
    otp = service.generate_otp()
    repository.store_otp(db, data.email, otp)
    send_otp_email(data.email, otp)
    return {"msg": "OTP sent for email verification"}

@router.post("/verify-email")
def verify_email(data: schema.VerifyEmailRequest, db: Session = Depends(get_db)):
    user = repository.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp_record = repository.verify_otp(db, data.email, data.otp)
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    repository.mark_user_verified(db, user)
    return JSONResponse(status_code=201,content={"msg": "Email verified successfully"})

@router.post("/login", response_model=schema.TokenResponse)
def login(data: schema.LoginRequest, db: Session = Depends(get_db)):
    user = repository.get_user_by_email(db, data.email)
    if not user or not service.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    token = service.create_jwt_token(user.id)
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="Lax",     # or "Strict" or "None"
        secure=False        # True in production (HTTPS only)
    )
    return response


@router.post("/verify-resend-otp")
def resend_otp(email: str, db: Session = Depends(get_db)):
    user = repository.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")

    otp = service.generate_otp()
    repository.update_otp(db, email, otp)

    send_otp_email(email, otp)
    print(otp)

    return {"msg": "OTP sent successfully"}

@router.post("/forgot-password")
def forgot_password(data: schema.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = repository.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    otp = service.generate_otp()
    repository.store_otp(db, data.email, otp)
    send_otp_email(data.email, otp)
    return {"msg": "OTP sent to your email for password reset"}


@router.put("/reset-password")
def reset_password(data: schema.ResetPasswordRequest, db: Session = Depends(get_db)):
    # Verify OTP
    valid = repository.verify_otp(db, data.email, data.otp)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Validate password strength
    if len(data.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not service.is_password_strong(data.new_password):
        raise HTTPException(status_code=400, detail="Weak password")

    # Update password
    hashed = service.get_password_hash(data.new_password)
    repository.update_user_password(db, data.email, hashed)
    return {"msg": "Password reset successful"}