
from datetime import datetime
from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from config.base_class import Base

class OrderInfo(Base):
    __tablename__ = 'order_infos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID, ForeignKey("users.id"), nullable=True)  # если авторизован
    session_id = Column(UUID, ForeignKey("session.session_id"), nullable=True)
    email = Column(String, nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    address_line1 = Column(String, nullable=False)
    city = Column(String, nullable=False)
    region = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    order_note = Column(Text, nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)
    # связь с пользователем
    user = relationship("User", back_populates="order_infos")
    session = relationship("Session", back_populates="order_infos")
    # связь с заказами
    orders = relationship("Order", back_populates="info")