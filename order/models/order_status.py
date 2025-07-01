from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from config.base_class import Base

class OrderStatus(Base):
    __tablename__ = 'order_statuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)  # Пример: "new", "paid", "shipped", "cancelled"
    description = Column(String(255), nullable=True)  # Можно хранить пояснение для админки или логов

    orders = relationship("Order", back_populates="status_rel")