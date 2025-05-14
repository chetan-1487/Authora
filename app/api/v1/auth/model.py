from sqlalchemy import Column, String, DateTime, Integer,ForeignKey
from ....db.base import Base
from datetime import datetime,timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer,nullable=False,primary_key=True)
    email = Column(String, index=True)
    otp = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime)