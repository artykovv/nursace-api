# models/verification_code.py

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timedelta
from uuid import uuid4
from config.base_class import Base

class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, index=True, nullable=False)
    code = Column(String(4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_verified = Column(Boolean, default=False)