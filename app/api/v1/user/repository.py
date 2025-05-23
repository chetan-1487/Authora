from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .model import User
from . import schema
from .schema import UpdateUserRequest
from ....utils.utils import save_profile_picture


async def update_user(db: AsyncSession, user_id: int, data: schema.UpdateUserRequest):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return None

    # Update name if provided
    if data.name:
        user.name = data.name

    # Handle profile picture update
    if data.profile_picture:
        profile_picture_name = save_profile_picture(
            data.profile_picture,
            existing_filename=user.profile_picture if user.profile_picture else None,
        )
        user.profile_picture = profile_picture_name

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
    for key, value in data.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
