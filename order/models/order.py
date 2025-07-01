
from datetime import datetime
from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship
from config.base_class import Base

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID, nullable=True)
    session_id = Column(UUID, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_price = Column(Numeric(10, 2))

    status_id = Column(Integer, ForeignKey("order_statuses.id"), default=1)  # default: "new"
    status_rel = relationship("OrderStatus", back_populates="orders")

    items = relationship("OrderItem", back_populates="order")

    info_id = Column(Integer, ForeignKey("order_infos.id"), nullable=False)
    info = relationship("OrderInfo", back_populates="orders")