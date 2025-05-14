from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal
from uuid import UUID

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    stock: Optional[int] = Field(default=0, ge=0)
    category_id: UUID  # use int if your DB uses int, UUID otherwise

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[UUID]

class ProductOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    price: Decimal
    stock: int
    category_id: UUID
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy → Pydantic
