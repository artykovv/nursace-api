from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class DiscountBase(BaseModel):
    name: str
    description: Optional[str]
    discount_percent: float
    start_date: datetime
    end_date: datetime
    is_active: bool = True


class DiscountCreate(DiscountBase):
    pass


class DiscountUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    discount_percent: Optional[float]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: Optional[bool]


class DiscountInDB(DiscountBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductIDs(BaseModel):
    product_ids: List[int]