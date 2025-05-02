from sqlalchemy.orm import Session
from .model import User, OTP
from datetime import datetime, timedelta

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, name: str, email: str, hashed_password: str):
    user = User(name=name, email=email, hashed_password=hashed_password)
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

