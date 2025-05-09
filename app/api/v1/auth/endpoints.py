from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from . import schema,service, repository
from ....core import security
from ....db.session import get_db
from ....services.mock_email_service import send_otp_email
from fastapi.responses import JSONResponse, RedirectResponse
from ....core import security
from ..auth.service import get_google_authorize_url, handle_google_callback
import os
import requests

router = APIRouter(
    tags=["User Registration"]
)

UPLOAD_DIR = "./uploaded_images/"

# Create the directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def is_url(value: str) -> bool:
    """
    Check if the provided string is a valid URL.
    """
    return value.startswith("http://") or value.startswith("https://")

def save_image_from_url(image_url: str) -> str:
    """
    Download image from a URL and save it locally.
    """
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # Create a unique filename based on the URL
            filename = str(uuid.uuid4()) + ".jpg"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            return file_path
        else:
            raise HTTPException(status_code=400, detail="Failed to download image from URL")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/auth/register")
def register(data: schema.RegisterRequest, db: Session = Depends(get_db)):
    if repository.get_user_by_email(db, data.email):
        raise HTTPException(status_code=200, detail="Email already registered")
    if not service.is_password_strong(data.password):
        raise HTTPException(status_code=400, detail="Weak password")
    if len(data.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    hashed = security.get_password_hash(data.password)
    profile_picture_path = save_profile_picture(data.profile_picture)
    user = repository.create_user(db, data.name, data.email, hashed,data.profile_picture)
    otp = service.generate_otp()
    repository.store_otp(db, data.email, otp)
    send_otp_email(data.email, otp)
    return {"msg": "OTP sent for email verification"}

@router.post("/auth/verify-email")
def verify_email(data: schema.VerifyEmailRequest, db: Session = Depends(get_db)):
    user = repository.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp_record = repository.verify_otp(db, data.email, data.otp)
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    repository.mark_user_verified(db, user)
    return JSONResponse(status_code=201,content={"msg": "Email verified successfully"})

@router.post("/auth/login", response_model=schema.TokenResponse)
def login(data: schema.LoginRequest, db: Session = Depends(get_db)):
    user = repository.get_user_by_email(db, data.email)
    if not user or not security.verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    token = security.create_access_token({"user_id": str(user.id)})
    
    response = JSONResponse(content={
        "message": "Login successful",
        "access_token": token,

    })

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="Lax",     # or "Strict" or "None"
        secure=False        # True in production (HTTPS only)
    )
    return response


@router.post("/auth/verify-resend-otp")
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

@router.post("/auth/forgot-password")
def forgot_password(data: schema.ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = repository.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    otp = service.generate_otp()
    repository.store_otp(db, data.email, otp)
    send_otp_email(data.email, otp)
    return {"msg": "OTP sent to your email for password reset"}


@router.put("/auth/reset-password")
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
    hashed = security.get_password_hash(data.new_password)
    repository.update_user_password(db, data.email, hashed)
    return {"msg": "Password reset successfully"}

@router.post("/logout")
def logout():
    """
    Client should discard the JWT token after calling this.
    """
    return {"message": "Successfully logged out. Please discard the token on the client."}


@router.get("/api/v1/auth/google/login")
def google_login():
    return RedirectResponse(get_google_authorize_url())

@router.get("/api/v1/auth/google/callback")
def google_callback(request: Request, db: Session = Depends(get_db)):
    return handle_google_callback(request,db)
