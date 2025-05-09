from sqlalchemy.orm import Session
from ..auth.model import User
from . import schema
from .schema import UpdateUserRequest

def update_user(db: Session, user_id: int, data: schema.UpdateUserRequest):
    user = db.query(User).filter(User.id == user_id).first()
    if data.name:
        user.name = data.name
    if data.profile_picture:
        user.profile_picture = data.profile_picture
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def update_user_in_db(user: User, data: UpdateUserRequest, db: Session):
    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user