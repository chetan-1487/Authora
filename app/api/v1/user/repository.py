from sqlalchemy.orm import Session
from ..auth.model import User
from . import schema
from .schema import UpdateUserRequest
from ....utils.utils import save_profile_picture

def update_user(db: Session, user_id: int, data: schema.UpdateUserRequest):
    user = db.query(User).filter(User.id == user_id).first()
    if data.name:
        user.name = data.name
    if user.profile_picture:
        profile_picture_name = save_profile_picture(user.profile_picture, existing_filename=user['profile_picture'])
        return {"message": "Profile picture updated", "file_path": profile_picture_name}
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