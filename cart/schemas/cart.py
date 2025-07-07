from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1
    session_id: UUID | None = None
    user_id: UUID | None = None

class ProductImageSchema(BaseModel):
    image_url: str
    is_main: bool
    order: int

    model_config = ConfigDict(from_attributes=True)

class Product(BaseModel):
    id: int = Field(alias='good_id')
    name: str = Field(alias='good_name')
    price: float = Field(alias='retail_price')
    retail_price_with_discount: Optional[float]

    images: List[ProductImageSchema] = []
    
    model_config = ConfigDict(from_attributes=True)
    
class CartItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    added_at: datetime
    product: Optional[Product]

    model_config = ConfigDict(from_attributes=True)