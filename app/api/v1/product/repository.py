from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from . import schema
from uuid import UUID
from .model import Product


# GET PRODUCTS (Only active)
async def get_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    category_id: UUID = None,
    min_price: float = None,
    max_price: float = None,
    search: str = None,
):
    query = select(Product).where(Product.is_active)

    filters = []
    if category_id:
        filters.append(Product.category_id == category_id)
    if min_price:
        filters.append(Product.price >= min_price)
    if max_price:
        filters.append(Product.price <= max_price)
    if search:
        filters.append(Product.name.ilike(f"{search}%"))

    if filters:
        query = query.where(and_(*filters))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


# GET SINGLE PRODUCT (Only active)
async def get_product(db: AsyncSession, id: UUID):
    result = await db.execute(
        select(Product).where(Product.id == id, Product.is_active)
    )
    if not result:
        raise HTTPException(status_code=404, detail="Invalid product ID")
    return result.scalar_one_or_none()


# CREATE PRODUCT
async def create_product(
    db: AsyncSession, data: schema.ProductCreate, image_url: str = None
):
    product = Product(**data.dict(), image_url=image_url, is_active=True)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


# UPDATE PRODUCT
async def update_product(
    db: AsyncSession, id: UUID, data: schema.ProductUpdate, image_url: str = None
):
    result = await db.execute(select(Product).where(Product.id == id))
    product = result.scalar_one_or_none()

    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(product, key, value)

    if image_url:
        product.image_url = image_url

    await db.commit()
    await db.refresh(product)
    return product


# SOFT DELETE PRODUCT
async def delete_product(db: AsyncSession, product_id: UUID):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    await db.commit()
    await db.refresh(product)
    return {"detail": "Product deleted"}
