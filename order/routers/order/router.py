from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from order.services.order import OrderStatusCRUD, OrderItemCRUD, OrderInfoCRUD, OrderCRUD
from order.schemas.order import (
    OrderStatusCreate, OrderStatusUpdate, OrderStatusResponse,
    OrderItemCreate, OrderItemUpdate, OrderItemResponse,
    OrderInfoCreate, OrderInfoUpdate, OrderInfoResponse,
    OrderCreate, OrderUpdate, OrderResponse
)
from uuid import UUID
from typing import List, Optional
from user.auth.fastapi_users_instance import fastapi_users
from user.auth.auth import auth_backend
from user.models import User

router = APIRouter(prefix="/orders", tags=["orders"])

# OrderStatus endpoints
@router.post("/statuses/", response_model=OrderStatusResponse)
async def create_status(
    status: OrderStatusCreate, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await OrderStatusCRUD.create(db, status)

@router.get("/statuses/{status_id}", response_model=OrderStatusResponse)
async def read_status(
    status_id: int, 
    db: AsyncSession = Depends(get_async_session)
):
    status = await OrderStatusCRUD.get(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Order status not found")
    return status

@router.get("/statuses/", response_model=List[OrderStatusResponse])
async def read_statuses(db: AsyncSession = Depends(get_async_session)):
    return await OrderStatusCRUD.get_all(db)

@router.put("/statuses/{status_id}", response_model=OrderStatusResponse)
async def update_status(
    status_id: int, 
    status: OrderStatusUpdate, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await OrderStatusCRUD.update(db, status_id, status)

@router.delete("/statuses/{status_id}")
async def delete_status(
    status_id: int, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    success = await OrderStatusCRUD.delete(db, status_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order status not found")
    return {"message": "Order status deleted"}

# OrderItem endpoints
@router.post("/items/", response_model=OrderItemResponse)
async def create_item(
    item: OrderItemCreate, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await OrderItemCRUD.create(db, item)

@router.get("/items/{item_id}", response_model=OrderItemResponse)
async def read_item(
    item_id: int, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    item = await OrderItemCRUD.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")
    return item

@router.get("/items/order/{order_id}", response_model=List[OrderItemResponse])
async def read_items(
    order_id: int, 
    db: AsyncSession = Depends(get_async_session)
):
    return await OrderItemCRUD.get_by_order(db, order_id)

@router.put("/items/{item_id}", response_model=OrderItemResponse)
async def update_item(
    item_id: int, 
    item: OrderItemUpdate, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await OrderItemCRUD.update(db, item_id, item)

@router.delete("/items/{item_id}")
async def delete_item(
    item_id: int, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    success = await OrderItemCRUD.delete(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order item not found")
    return {"message": "Order item deleted"}

# OrderInfo endpoints
@router.post("/info/", response_model=OrderInfoResponse)
async def create_info(
    info: OrderInfoCreate, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await OrderInfoCRUD.create(db, info)

@router.get("/info/{info_id}", response_model=OrderInfoResponse)
async def read_info(info_id: int, db: AsyncSession = Depends(get_async_session)):
    info = await OrderInfoCRUD.get(db, info_id)
    if not info:
        raise HTTPException(status_code=404, detail="Order info not found")
    return info

@router.get("/info/", response_model=List[OrderInfoResponse])
async def read_infos(db: AsyncSession = Depends(get_async_session)):
    return await OrderInfoCRUD.get_all(db)

@router.put("/info/{info_id}", response_model=OrderInfoResponse)
async def update_info(
    info_id: int, 
    info: OrderInfoUpdate, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await OrderInfoCRUD.update(db, info_id, info)

@router.delete("/info/{info_id}")
async def delete_info(
    info_id: int, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    success = await OrderInfoCRUD.delete(db, info_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order info not found")
    return {"message": "Order info deleted"}

# Order endpoints
@router.post("/", response_model=OrderResponse)
async def create_order_endpoint(
    order: OrderCreate, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await OrderCRUD.create(db, order)

@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(order_id: int, db: AsyncSession = Depends(get_async_session)):
    order = await OrderCRUD.get(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/", response_model=List[OrderResponse])
async def read_orders(
    user_id: Optional[UUID] = None,
    session_id: Optional[UUID] = None,
    sort_by_id: Optional[str] = Query(None, regex="^(asc|desc)$"),
    sort_by_price: Optional[str] = Query(None, regex="^(asc|desc)$"),
    sort_by_date: Optional[str] = Query(None, regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_async_session)
):
    return await OrderCRUD.get_all(db, user_id, session_id, sort_by_id, sort_by_price, sort_by_date)

@router.put("/{order_id}", response_model=OrderResponse)
async def update_order_endpoint(
    order_id: int, 
    order: OrderUpdate, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await OrderCRUD.update(db, order_id, order)

@router.delete("/{order_id}")
async def delete_order_endpoint(
    order_id: int, 
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    success = await OrderCRUD.delete(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted"}