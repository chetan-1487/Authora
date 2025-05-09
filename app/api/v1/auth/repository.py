from fastapi import Depends
from sqlalchemy.orm import Session
from .model import User, OTP
from datetime import datetime, timedelta
from ....db.session import get_db
from ....core.security import get_password_hash
from ....utils.utils import save_profile_picture

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, name: str, email: str, hashed_password: str, profile_picture: str = None):
    user = User(name=name, email=email, hashed_password=hashed_password,profile_picture=profile_picture)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def store_otp(db: Session, email: str, otp: str):
    expiry = datetime.utcnow() + timedelta(minutes=10)
    db.add(OTP(email=email, otp=otp, expires_at=expiry))
    db.commit()

def update_otp(db: Session, email: str, otp: str):
    expiry = datetime.utcnow() + timedelta(minutes=10)
    db.query(OTP).filter(OTP.email == email).update({"otp": otp, "expires_at": expiry})
    db.commit()

def verify_otp(db: Session, email: str, otp: str):
    return db.query(OTP).filter(
        OTP.email == email,
        OTP.otp == otp,
        OTP.expires_at > datetime.utcnow()
    ).first()

def mark_user_verified(db: Session, user: User):
    user.is_verified = True
    db.commit()

def update_user_password(db: Session, email: str, new_hashed_pw: str):
    user = get_user_by_email(db, email)
    if user:
        user.hashed_password = new_hashed_pw
        db.commit()

def get_or_create_user_from_google(user_info: dict, db: Session) -> User:
    email = user_info["email"]
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # User doesn't exist, create a new user
        user = User(
            email=email,
            name=user_info.get("name"),
            profile_picture=user_info.get("picture"),
            is_verified=True,
            auth_provider="google",
            hashed_password=get_password_hash("Hello@123")  # or generate a secure password if needed
        )
        save_profile_picture(user_info.get("picture"))  # Save profile picture if needed
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # User exists, update the user's information if changed
        user.name = user_info.get("name", user.name)  # Update name if provided
        user.profile_picture = user_info.get("picture", user.profile_picture)  # Update profile picture if provided
        user.is_verified = True  # You can also update verification status if needed
        user.auth_provider = "google"  # Ensure the auth provider is set as 'google'
        
        # Commit changes if any information was updated
        db.commit()
        db.refresh(user)

    return user