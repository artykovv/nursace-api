from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import UUID, ForeignKey, Integer, Table, Column, DateTime, String, func
from sqlalchemy.orm import relationship

from config.base_class import Base

# Таблица связи многие-ко-многим для пользователей и филиалов
user_branches = Table(
    'user_branches',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('branch_id', Integer, ForeignKey('branches.id'), primary_key=True),
)

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = 'users'
    
    name = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    register_at = Column(DateTime, nullable=True)
    session_id = Column(UUID(as_uuid=True), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    branches = relationship("Branch", secondary="user_branches", back_populates="users")

    order_infos = relationship("OrderInfo", back_populates="user")

