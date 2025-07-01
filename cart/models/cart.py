from datetime import datetime
from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from config.base_class import Base

class CartItem(Base):
    __tablename__ = 'cart_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(UUID, nullable=True, index=True)
    user_id = Column(UUID, nullable=True, index=True)  # если у вас есть User

    product_id = Column(Integer, ForeignKey("products.good_id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")

    __table_args__ = (
        UniqueConstraint('session_id', 'product_id', name='uq_session_product'),
    )