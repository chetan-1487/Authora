from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    UploadFile,
    File,
    Form,
    Response,
    Cookie,
)
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from . import schema, repository
from ....core.security import (
    verify_password,
    create_access_token,
    get_password_hash,
    decode_token,
)
from ....db.session import get_db
from ....services.mock_email_service import send_otp_email
from fastapi.responses import JSONResponse, RedirectResponse
from .service import get_google_authorize_url
from ....utils.utils import generate_otp
from .repository import handle_google_callback
from pydantic import EmailStr
from ....core.security import validate_password_strength
from ....services.s3_service import save_profile_info

router = APIRouter(tags=["User Registration"])


@router.post("/auth/register")
async def register(
    name: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...),
    profile_picture: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        validate_password_strength(password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    user = await repository.get_user_by_email(db, email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(password)
    profile_picture_name = await save_profile_info(profile_picture)

    # Pass saved image path (not file object) to DB
    await repository.create_user(db, name, email, hashed_password, profile_picture_name)

    otp = generate_otp()
    await repository.store_otp(db, email, otp)
    await send_otp_email(email, otp)

    return {"msg": "OTP sent for email verification"}


@router.post("/auth/verify-email")
async def verify_email(
    data: schema.VerifyEmailRequest, db: AsyncSession = Depends(get_db)
):
    user = await repository.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp_record = await repository.verify_otp(db, data.email, data.otp)
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    await repository.mark_user_verified(db, user)
    return JSONResponse(status_code=201, content={"msg": "Email verified successfully"})


@router.post("/auth/login", response_model=schema.TokenResponse)
async def login(
    data: schema.LoginRequest,
    db: AsyncSession = Depends(get_db),
    access_token: str = Cookie(default=None),
):

    if access_token:
        try:
            payload = decode_token(access_token)
            if payload.get("user_id"):
                raise HTTPException(status_code=400, detail="User already logged in")
        except JWTError:
            pass

    user = await repository.get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")
    token = create_access_token({"user_id": str(user.id)})

    response = JSONResponse(
        content={
            "message": "Login successful",
            "access_token": token,
        }
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="Lax",  # or "Strict" or "None"
        secure=False,  # True in production (HTTPS only)
    )
    return response


@router.post("/auth/verify-resend-otp")
async def resend_otp(email: str, db: AsyncSession = Depends(get_db)):
    user = await repository.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        raise HTTPException(status_code=400, detail="User is already verified")

    otp = generate_otp()
    await repository.update_otp(db, email, otp)

    await send_otp_email(email, otp)

    return {"msg": "OTP sent successfully"}


@router.post("/auth/forgot-password")
async def forgot_password(
    data: schema.ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
):
    user = await repository.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    otp = generate_otp()
    await repository.store_otp(db, data.email, otp)
    await send_otp_email(data.email, otp)
    return {"msg": "OTP sent to your email for password reset"}


@router.post("/auth/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"msg": "Logout successful"}


@router.put("/auth/reset-password")
async def reset_password(
    data: schema.ResetPasswordRequest, db: AsyncSession = Depends(get_db)
):
    # Verify OTP
    valid = await repository.verify_otp(db, data.email, data.otp)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    try:
        validate_password_strength(data.new_password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Update password
    hashed = get_password_hash(data.new_password)
    await repository.update_user_password(db, data.email, hashed)
    return {"msg": "Password reset successfully"}


@router.get("/api/v1/auth/google/login")
async def google_login():
    return RedirectResponse(get_google_authorize_url())


@router.get("/api/v1/auth/google/callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    return await handle_google_callback(request, db)
