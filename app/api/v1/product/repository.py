from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
from . import model, schema
from uuid import UUID


async def get_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    category_id: UUID = None,
    min_price: float = None,
    max_price: float = None
):
    query = select(model.Product)

    filters = []
    if category_id is not None:
        filters.append(model.Product.category_id == category_id)
    if min_price is not None:
        filters.append(model.Product.price >= min_price)
    if max_price is not None:
        filters.append(model.Product.price <= max_price)

    if filters:
        query = query.where(and_(*filters))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_product(db: AsyncSession, id: UUID):
    result = await db.execute(select(model.Product).where(model.Product.id == id))
    return result.scalar_one_or_none()

async def create_product(db: AsyncSession, data: schema.ProductCreate, image_url: str = None):
    product = model.Product(**data.dict(), image_url=image_url)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product

async def update_product(db: AsyncSession, id: int, data: schema.ProductUpdate, image_url: str = None):
    result = await db.execute(select(model.Product).where(model.Product.id == id))
    product = result.scalar_one_or_none()

    if not product:
        return None

    for key, value in data.dict(exclude_unset=True).items():
        setattr(product, key, value)

    if image_url:
        product.image_url = image_url

    await db.commit()
    await db.refresh(product)
    return product

async def delete_product(db: AsyncSession, id: int):
    result = await db.execute(select(model.Product).where(model.Product.id == id))
    product = result.scalar_one_or_none()

    if not product:
        return False

    await db.delete(product)
    await db.commit()
    return True
