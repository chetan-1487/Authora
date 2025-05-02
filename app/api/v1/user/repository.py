from sqlalchemy.orm import Session
from ..auth.model import User
from . import schema

def update_user(db: Session, user_id: int, data: schema.UpdateUserRequest):
    user = db.query(User).filter(User.id == user_id).first()
    if data.name:
        user.name = data.name
    if data.email:
        user.email = data.email
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()