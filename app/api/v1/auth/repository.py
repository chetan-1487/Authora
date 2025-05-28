from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from .model import OTP
from sqlalchemy.future import select
from datetime import datetime, timedelta
from ....core.security import get_password_hash, create_access_token
import httpx
from ....core.config import settings
from fastapi.responses import JSONResponse
from ..user.model import User
from ....services.s3_service import save_profile_info
import aiohttp
from fastapi import UploadFile
from io import BytesIO


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

    async def fetch_and_upload_profile_picture(picture_url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(picture_url) as response:
                if response.status == 200:
                    content = await response.read()
                    filename = "google_profile.jpg"  # arbitrary name
                    file = UploadFile(
                        filename=filename,
                        file=BytesIO(content),
                        content_type="image/jpeg",
                    )
                    return await save_profile_info(file)
                return None

    if not user:
        # Create new user
        uploaded_url = await fetch_and_upload_profile_picture(user_info.get("picture"))
        user = User(
            email=email,
            name=user_info.get("name"),
            profile_picture=uploaded_url,
            is_verified=True,
            auth_provider="google",
            hashed_password=get_password_hash("Hello@123"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Existing user, update fields
        user.name = user_info.get("name", user.name)

        new_picture_url = user_info.get("picture")
        if new_picture_url and new_picture_url != user.profile_picture:
            uploaded_url = await fetch_and_upload_profile_picture(new_picture_url)
            if uploaded_url:
                user.profile_picture = uploaded_url

        user.is_verified = True
        user.auth_provider = "google"

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
