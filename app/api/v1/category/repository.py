from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .model import Category
from ..product.model import Product
from . import schema
from uuid import UUID


async def get_all_categories(db: AsyncSession):
    result = await db.execute(select(Category))
    return result.scalars().all()


async def get_category(db: AsyncSession, id: UUID):
    result = await db.execute(select(Category).where(Category.id == id))
    if not result:
        raise HTTPException(status_code=404, detail="Invalid product ID")
    return result.scalar_one_or_none()


async def create_category(db: AsyncSession, data: schema.CategoryCreate):
    # Check if category already exists
    result = await db.execute(select(Category).where(Category.name == data.name))
    existing_category = result.scalar_one_or_none()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists.",
        )
    # Create and insert new category
    category = Category(**data.dict())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def update_category(db: AsyncSession, id: UUID, data: schema.CategoryUpdate):
    result = await db.execute(select(Category).where(Category.id == id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(category, key, value)

    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, id: UUID):
    # Step 1: Check if any products are linked to the category
    product_check = await db.execute(select(Product).where(Product.category_id == id))
    if product_check.first():  # Product(s) found
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category. Products exist in this category.",
        )

    # Step 2: Retrieve the category
    result = await db.execute(select(Category).where(Category.id == id))
    category = result.scalar_one_or_none()
    if not category:
        return False

    # Step 3: Delete and commit
    await db.delete(category)
    await db.commit()
    return True
