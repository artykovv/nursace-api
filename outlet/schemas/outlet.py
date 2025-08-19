from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class OutletBase(BaseModel):
    name: str
    description: Optional[str]
    discount_percent: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True


class OutletCreate(OutletBase):
    pass


class OutletUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    discount_percent: Optional[float]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: Optional[bool]


class OutletInDB(OutletBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class ProductIDs(BaseModel):
    product_ids: List[int]


