from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Lead Schemas
class LeadBase(BaseModel):
    full_name: str
    phone_number: str
    comment: Optional[str] = None
    status_id: Optional[int] = None

class LeadCreate(LeadBase):
    product_ids: list[int] = Field(default_factory=list)

class LeadUpdate(LeadBase):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

class LeadRead(LeadBase):
    id: int
    created_at: datetime
    status: Optional["LeadStatusRead"] = None
    products: List["LeadProductRead"] = []

    class Config:
        orm_mode = True

# LeadProduct Schemas
class LeadProductBase(BaseModel):
    lead_id: int
    product_id: Optional[int] = None
    quantity: int = 1

class LeadProductCreate(LeadProductBase):
    pass

class LeadProductUpdate(LeadProductBase):
    lead_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None


class BaseProductSchema(BaseModel):
    id: int = Field(alias='good_id')
    name: str = Field(alias='good_name')
    price: float = Field(alias='retail_price')
    retail_price_with_discount: Optional[float]
    articul: Optional[str]

class LeadProductRead(LeadProductBase):
    id: int
    product: Optional["BaseProductSchema"]
    class Config:
        orm_mode = True

# LeadStatus Schemas
class LeadStatusBase(BaseModel):
    name: str

class LeadStatusCreate(LeadStatusBase):
    pass

class LeadStatusUpdate(LeadStatusBase):
    name: Optional[str] = None

class LeadStatusRead(LeadStatusBase):
    id: int

    class Config:
        orm_mode = True