from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from config.base_class import Base

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связь со статусами
    status_id = Column(Integer, ForeignKey("lead_statuses.id"), nullable=True)
    status = relationship("LeadStatus")

    products = relationship("LeadProduct", back_populates="lead", cascade="all, delete-orphan")


class LeadProduct(Base):
    __tablename__ = "lead_products"

    id = Column(Integer, primary_key=True, index=True)

    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.good_id", ondelete="SET NULL"))

    quantity = Column(Integer, default=1)

    lead = relationship("Lead", back_populates="products")
    product = relationship("Product", back_populates="lead_products")

class LeadStatus(Base):
    __tablename__ = "lead_statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # Пример: "Новый", "В работе", "Успешно", "Отказ"