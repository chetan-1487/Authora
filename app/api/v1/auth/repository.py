from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from .model import OTP
from sqlalchemy.future import select
from datetime import datetime, timedelta
from ....core.security import get_password_hash, create_access_token
from ....utils.utils import save_profile_picture_from_url
import httpx
from ....core.config import settings
from fastapi.responses import JSONResponse
from ..user.model import User


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(
    db: AsyncSession,
    name: str,
    email: str,
    hashed_password: str,
    profile_picture: str = None,
):
    user = User(
        name=name,
        email=email,
        hashed_password=hashed_password,
        profile_picture=profile_picture,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def store_otp(db: AsyncSession, email: str, otp: str):
    expiry = datetime.utcnow() + timedelta(minutes=10)
    db.add(OTP(email=email, otp=otp, expires_at=expiry))
    await db.commit()


async def update_otp(db: AsyncSession, email: str, otp: str):
    expiry = datetime.utcnow() + timedelta(minutes=10)
    await db.execute(
        OTP.__table__.update()
        .where(OTP.email == email)
        .values(otp=otp, expires_at=expiry)
    )
    await db.commit()


async def verify_otp(db: AsyncSession, email: str, otp: str):
    stmt = select(OTP).where(OTP.email == email, OTP.otp == otp)
    result = await db.execute(stmt)
    return result.scalars().first()


async def mark_user_verified(db: AsyncSession, user: User):
    user.is_verified = True
    await db.commit()


async def update_user_password(db: AsyncSession, email: str, new_hashed_pw: str):
    user = await get_user_by_email(db, email)
    if user:
        user.hashed_password = new_hashed_pw
        await db.commit()


async def get_or_create_user_from_google(user_info: dict, db: AsyncSession) -> User:
    email = user_info["email"]
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if not user:
        # User doesn't exist, create a new user
        user = User(
            email=email,
            name=user_info.get("name"),
            profile_picture=user_info.get("picture"),
            is_verified=True,
            auth_provider="google",
            hashed_password=get_password_hash(
                "Hello@123"
            ),  # or generate a secure password if needed
        )
        await save_profile_picture_from_url(
            user_info.get("picture")
        )  # Save profile picture if needed
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # User exists, update the user's information if changed
        user.name = user_info.get("name", user.name)  # Update name if provided
        user.profile_picture = user_info.get(
            "picture", user.profile_picture
        )  # Update profile picture if provided
        user.is_verified = True  # You can also update verification status if needed
        user.auth_provider = "google"  # Ensure the auth provider is set as 'google'

        # Commit changes if any information was updated
        await db.commit()
        await db.refresh(user)

    return user


async def handle_google_callback(request: Request, db: AsyncSession):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_json = token_res.json()
        id_token = token_json.get("id_token")

        if not id_token:
            return JSONResponse({"error": "Missing ID token"}, status_code=400)

        user_info_res = await client.get(
            f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={id_token}"
        )
        user_info = user_info_res.json()

    user = await get_or_create_user_from_google(user_info, db)

    jwt_token = create_access_token({"user_id": str(user.id)})

    response = JSONResponse(
        content={"message": "Google login successful", "access_token": jwt_token}
    )

    response.set_cookie(
        key="access_token",
        value=jwt_token,
        httponly=True,
        samesite="Lax",  # Use "None" + secure=True if using cross-site cookies
        secure=False,  # Use True in production (HTTPS)
    )
    return response
