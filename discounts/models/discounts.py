from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from config.base_class import Base
from sqlalchemy.orm import relationship

class Discount(Base):
    __tablename__ = 'discounts'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(500))
    discount_percent = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    products = relationship("DiscountProduct", back_populates="discount")

class DiscountProduct(Base):
    __tablename__ = 'discount_products'

    id = Column(Integer, primary_key=True)
    discount_id = Column(Integer, ForeignKey("discounts.id"))
    product_id = Column(Integer, ForeignKey("products.good_id"))

    discount = relationship("Discount", back_populates="products")
    product = relationship("Product", back_populates="discounts")