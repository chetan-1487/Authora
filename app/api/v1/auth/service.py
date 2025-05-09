import random, string
import re
from app.api.v1.auth.repository import get_or_create_user_from_google
import requests
from app.core.config import settings
from urllib.parse import urlencode
from fastapi.responses import JSONResponse
from ....core.security import create_access_token
from fastapi import Request
from sqlalchemy.orm import Session
from .model import User

def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))


def is_password_strong(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    if not re.search(r'[@$!%*?&]', password):
        return False
    return True

def get_google_authorize_url():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

def handle_google_callback(request: Request, db: Session):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)

    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
    ).json()

    id_token = token_res.get("id_token")
    user_info = requests.get(
        f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={id_token}"
    ).json()

    user = get_or_create_user_from_google(user_info,db)
    user_data=db.query(User).filter(User.email == user_info["email"]).first()
    # user = repository.get_user_by_email(db, data.email)
    jwt_token = create_access_token({"user_id": str(user_data.id)})
    return {"access_token": jwt_token, "token_type": "bearer"}