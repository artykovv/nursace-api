from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from .user import user_branches

from config.base_class import Base

# Модель филиалов (Branches)
class Branch(Base):
    __tablename__ = 'branches'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    users = relationship("User", secondary=user_branches, back_populates="branches")