from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID as uuid


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


class CategoryOut(BaseModel):
    id: uuid
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
