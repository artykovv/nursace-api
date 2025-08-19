from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from config.base_class import Base
from sqlalchemy.orm import relationship


class Outlet(Base):
    __tablename__ = "outlets"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    discount_percent = Column(Float, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    products = relationship("OutletProduct", back_populates="outlet")


class OutletProduct(Base):
    __tablename__ = "outlet_products"

    id = Column(Integer, primary_key=True)
    outlet_id = Column(Integer, ForeignKey("outlets.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.good_id"), nullable=False)

    outlet = relationship("Outlet", back_populates="products")
    product = relationship("Product", back_populates="outlets")