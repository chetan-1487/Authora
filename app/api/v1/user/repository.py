from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .model import User
from typing import Optional
from fastapi import UploadFile
from .schema import UpdateUserRequest
from ....services.s3_service import save_profile_info


async def update_user(
    db: AsyncSession,
    user_id: int,
    name: Optional[str],
    profile_picture: Optional[UploadFile],
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return None

    if name:
        user.name = name

    if profile_picture:
        profile_picture_url = await save_profile_info(profile_picture)
        user.profile_picture = profile_picture_url

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        await db.delete(user)
        await db.commit()


async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user_in_db(user: User, data: UpdateUserRequest, db: AsyncSession):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
