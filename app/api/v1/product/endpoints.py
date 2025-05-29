from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ....db.session import get_db
from . import schema, repository
from ....services.s3_service import save_product_image
from ..user.service import get_current_user
from ..user.model import User
from uuid import UUID
from sqlalchemy import select
from ..category.model import Category
from typing import Optional
from .repository import delete_product
from .model import Product
import csv
from io import StringIO
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(tags=["Products"])


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(StringIO(decoded))

    required_fields = {"name", "price", "stock", "category_id"}
    if not required_fields.issubset(reader.fieldnames):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must include columns: {', '.join(required_fields)}",
        )

    added = 0
    skipped = 0
    for row in reader:
        try:
            name = row["name"].strip()
            category_id = UUID(row["category_id"])
            # Check if product already exists
            existing = await db.execute(
                select(Product).where(
                    Product.name == name, Product.category_id == category_id
                )
            )
            existing_product = existing.scalar_one_or_none()

            if existing_product:
                skipped += 1
                continue

            product = Product(
                name=name,
                price=float(row["price"]),
                stock=int(row["stock"]),
                category_id=category_id,
                description=row.get("description", "").strip() or None,
                image_url=row.get("image_url", "").strip() or None,
                is_active=row.get("is_active", "true").strip().lower() == "true",
            )
            db.add(product)
            added += 1
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error in row: {row} — {e}")

    try:
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"message": f"{added} products uploaded successfully", "skipped": skipped}


@router.get("/products", response_model=list[schema.ProductOut])
async def list_products(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    category_id: Optional[UUID] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    search: Optional[str] = Query(None),
    user: User = Depends(get_current_user),
):
    return await repository.get_products(
        db, skip, limit, category_id, min_price, max_price, search
    )


@router.get("/product/{product_id}", response_model=schema.ProductOut)
async def get_product(
    id: UUID, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    product = await repository.get_product(db, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/product/", response_model=schema.ProductOut)
async def create_product(
    product_data: schema.ProductCreate = Depends(schema.ProductCreate.as_form),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    image_url = await save_product_image(image) if image else None
    if product_data.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0")
    result = await db.execute(
        select(Category).where(Category.id == product_data.category_id)
    )
    category = result.scalars().first()

    if not category:
        raise HTTPException(status_code=400, detail="Category ID is not valid")
    new_product = await repository.create_product(db, product_data, image_url)
    return new_product


@router.put("/product/{product_id}", response_model=schema.ProductOut)
async def update_product(
    id: UUID,
    product_data: schema.ProductUpdate = Depends(schema.ProductUpdate.as_form),
    image: Optional[UploadFile] = File(None),  # Optional
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    image_url = None
    if image and image.filename:  # Only upload if a real file is given
        image_url = await save_product_image(image)

    product = await repository.update_product(db, id, product_data, image_url)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/product/{product_id}")
async def delete_product_with_id(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await delete_product(db, product_id)
    return {"detail": "Product deleted."}
