from sqlalchemy import Column, String, DateTime, Integer
from ....db.base import Base
from datetime import datetime, timezone


class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, nullable=False, primary_key=True)
    email = Column(String, index=True)
    otp = Column(String)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    expires_at = Column(DateTime)
