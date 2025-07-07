from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional
from decimal import Decimal

# OrderStatus
class OrderStatusBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrderStatusCreate(OrderStatusBase):
    pass

class OrderStatusUpdate(OrderStatusBase):
    name: Optional[str] = None

class OrderStatusResponse(OrderStatusBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# OrderItem
class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price: Decimal

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = None
    price: Optional[Decimal] = None

class OrderItemResponse(OrderItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

# OrderInfo
class OrderInfoBase(BaseModel):
    user_id: Optional[UUID] = None
    email: str
    first_name: str
    last_name: str
    address_line1: str
    city: str
    region: str
    postal_code: str
    phone: str
    order_note: Optional[str] = None

class OrderInfoCreate(OrderInfoBase):
    pass

class OrderInfoUpdate(OrderInfoBase):
    user_id: Optional[UUID] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address_line1: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    order_note: Optional[str] = None

class OrderInfoResponse(OrderInfoBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Order
class OrderBase(BaseModel):
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    total_price: Optional[Decimal] = None
    status_id: Optional[int] = 1
    info_id: int

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    total_price: Optional[Decimal] = None
    status_id: Optional[int] = None
    info_id: Optional[int] = None

class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    items: list[OrderItemResponse] = []
    status: Optional[OrderStatusResponse] = None
    info: Optional[OrderInfoResponse] = None

    model_config = ConfigDict(from_attributes=True)

class ChekoutOrderCreate(BaseModel):
    user_id: UUID | None = None
    session_id: UUID | None = None
    email: str
    first_name: str
    last_name: str
    address_line1: str
    city: str
    region: str
    postal_code: str
    phone: str
    order_note: str | None = None
    is_save: bool | None = None