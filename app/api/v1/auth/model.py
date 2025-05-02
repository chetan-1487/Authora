from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from ....db.base import Base
from datetime import datetime
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,index=True)
    name = Column(String,nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String,nullable=False)
    is_verified = Column(Boolean, default=False)

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer,nullable=False,primary_key=True)
    email = Column(String, index=True)
    otp = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
