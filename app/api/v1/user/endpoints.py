from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from . import repository, schema
from .service import get_db, get_current_user

router = APIRouter(tags=["User_Information"])


@router.get("/user/info", response_model=schema.UserResponse)
async def get_user_info(current_user=Depends(get_current_user)):
    return current_user


@router.patch("/user/update", response_model=schema.UserResponse)
async def update_user_info(
    data: schema.UpdateUserRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    updated_user = await repository.update_user(db, current_user.id, data)
    return updated_user


@router.delete("/user/delete")
async def delete_user_account(
    db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)
):
    await repository.delete_user(db, current_user.id)
    return {"msg": "User deleted successfully"}
