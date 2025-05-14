from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ....db.session import get_db
from . import schema, repository
from ....utils.utils import save_product_image
from ..user.service import get_current_user

router = APIRouter(
    tags=["Products"]
)

@router.get("/products", response_model=list[schema.ProductOut])
async def list_products(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
    category_id: int = Query(None),
    min_price: float = Query(None),
    max_price: float = Query(None)
):
    return await repository.get_products(db, skip, limit, category_id, min_price, max_price)

@router.get("/products/{id}", response_model=schema.ProductOut)
async def get_product(id: int, db: AsyncSession = Depends(get_db)):
    product = await repository.get_product(db, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products/", response_model=schema.ProductOut)
async def create_product(
    product_data: schema.ProductCreate,
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    image_url = await save_product_image(image) if image else None
    return await repository.create_product(db, product_data, image_url)

@router.put("/products/{id}", response_model=schema.ProductOut)
async def update_product(
    id: int,
    product_data: schema.ProductUpdate,
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):
    image_url = await save_product_image(image) if image else None
    product = await repository.update_product(db, id, product_data, image_url)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/products/{id}")
async def delete_product(id: int, db: AsyncSession = Depends(get_db)):
    success = await repository.delete_product(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"detail": "Product deleted"}
