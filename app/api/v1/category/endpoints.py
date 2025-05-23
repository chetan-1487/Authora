from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ....db.session import get_db
from . import schema, repository
from ..user.service import get_current_user
from ..user.model import User
from uuid import UUID

router = APIRouter(tags=["Categories"])


@router.get("/categories", response_model=list[schema.CategoryOut])
async def list_categories(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    return await repository.get_all_categories(db)


@router.get("/category/{id}", response_model=schema.CategoryOut)
async def get_category(
    id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    category = await repository.get_category(db, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/category", response_model=schema.CategoryOut)
async def create_category(
    data: schema.CategoryCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    new_category = await repository.create_category(db, data)
    return new_category


@router.put("/category/{id}", response_model=schema.CategoryOut)
async def update_category(
    id: UUID,
    data: schema.CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    category = await repository.update_category(db, id, data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/category/{id}")
async def delete_category(
    id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    success = await repository.delete_category(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"detail": "Category deleted"}
