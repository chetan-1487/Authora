from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID as uuid

class CategoryCreate(BaseModel):
    name: str
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
