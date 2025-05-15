from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ....db.session import get_db
from . import schema, repository
from ....utils.utils import save_product_image
from ..user.service import get_current_user
from ..user.model import User
from uuid import UUID
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import uuid

router = APIRouter(
    tags=["Products"]
)

@router.get("/products", response_model=list[schema.ProductOut])
async def list_products(db: AsyncSession = Depends(get_db), skip: int = 0, limit: int = 10, category_id: UUID = Query(None), min_price: float = Query(None), max_price: float = Query(None), user: User = Depends(get_current_user)):
    return await repository.get_products(db, skip, limit, category_id, min_price, max_price)

@router.get("/products/{id}", response_model=schema.ProductOut)
async def get_product(id: UUID, db: AsyncSession = Depends(get_db),user: User = Depends(get_current_user)):
    product = await repository.get_product(db, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/products/", response_model=schema.ProductOut)
async def create_product(product_data: schema.ProductCreate = Depends(schema.ProductCreate.as_form), image: UploadFile = File(None), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    image_url = await save_product_image(image) if image else None
    new_product= await repository.create_product(db, product_data, image_url)
    return new_product

@router.put("/products/{id}", response_model=schema.ProductOut)
async def update_product(id: UUID, product_data: schema.ProductUpdate = Depends(schema.ProductUpdate.as_form), image: UploadFile = File(None), db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    image_url = await save_product_image(image) if image else None
    product = await repository.update_product(db, id, product_data, image_url)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.delete("/products/{id}")
async def delete_product(id: UUID, db: AsyncSession = Depends(get_db),user: User = Depends(get_current_user)):
    success = await repository.delete_product(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"detail": "Product deleted"}

signed_urls = {}

@router.post("/upload")
async def upload_image(file: UploadFile):
    signed_url = await save_product_image(file)
    image_id = str(uuid.uuid4())
    signed_urls[image_id] = {
        "url": signed_url,
        "created_at": datetime.utcnow(),
        "expires_in": timedelta(seconds=1)  # 5 minutes
    }
    return {"image_id": image_id}