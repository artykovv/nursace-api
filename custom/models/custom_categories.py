from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from config.base_class import Base

product_custom_category = Table(
    "product_custom_category",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.good_id", ondelete="CASCADE")),
    Column("custom_category_id", Integer, ForeignKey("custom_categories.category_id", ondelete="CASCADE"))
)

class CustomCategory(Base):
    __tablename__ = 'custom_categories'
    
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String(255), nullable=False)
    
    products = relationship("Product", secondary=product_custom_category, back_populates="custom_categories")