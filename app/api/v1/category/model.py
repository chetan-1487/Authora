from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import relationship
from ....db.base import Base
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Category(Base):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    products = relationship("Product", back_populates="category", cascade="all, delete")
