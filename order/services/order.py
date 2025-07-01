from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from order.models import OrderStatus, OrderItem, OrderInfo, Order
from order.schemas.order import (
    OrderStatusCreate, OrderStatusUpdate,
    OrderItemCreate, OrderItemUpdate,
    OrderInfoCreate, OrderInfoUpdate,
    OrderCreate, OrderUpdate
)
from uuid import UUID
from typing import List, Optional

class OrderStatusCRUD:
    """CRUD operations for OrderStatus model"""
    
    @staticmethod
    async def create(db: AsyncSession, status: OrderStatusCreate) -> OrderStatus:
        db_status = OrderStatus(**status.dict())
        db.add(db_status)
        await db.commit()
        await db.refresh(db_status)
        return db_status

    @staticmethod
    async def get(db: AsyncSession, status_id: int) -> Optional[OrderStatus]:
        result = await db.execute(select(OrderStatus).filter(OrderStatus.id == status_id))
        return result.scalars().first()
    
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[OrderStatus]:
        result = await db.execute(select(OrderStatus).filter(OrderStatus.name == name))
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[OrderStatus]:
        result = await db.execute(select(OrderStatus))
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, status_id: int, status_update: OrderStatusUpdate) -> Optional[OrderStatus]:
        db_status = await OrderStatusCRUD.get(db, status_id)
        if not db_status:
            raise HTTPException(status_code=404, detail="Order status not found")
        
        for key, value in status_update.dict(exclude_unset=True).items():
            setattr(db_status, key, value)
        
        await db.commit()
        await db.refresh(db_status)
        return db_status

    @staticmethod
    async def delete(db: AsyncSession, status_id: int) -> bool:
        db_status = await OrderStatusCRUD.get(db, status_id)
        if not db_status:
            return False
        await db.delete(db_status)
        await db.commit()
        return True

class OrderItemCRUD:
    """CRUD operations for OrderItem model"""
    
    @staticmethod
    async def create(db: AsyncSession, item: OrderItemCreate) -> OrderItem:
        db_item = OrderItem(**item.dict())
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def get(db: AsyncSession, item_id: int) -> Optional[OrderItem]:
        result = await db.execute(select(OrderItem).filter(OrderItem.id == item_id))
        return result.scalars().first()

    @staticmethod
    async def get_by_order(db: AsyncSession, order_id: int) -> List[OrderItem]:
        result = await db.execute(select(OrderItem).filter(OrderItem.order_id == order_id))
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, item_id: int, item_update: OrderItemUpdate) -> Optional[OrderItem]:
        db_item = await OrderItemCRUD.get(db, item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Order item not found")
        
        for key, value in item_update.dict(exclude_unset=True).items():
            setattr(db_item, key, value)
        
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def delete(db: AsyncSession, item_id: int) -> bool:
        db_item = await OrderItemCRUD.get(db, item_id)
        if not db_item:
            return False
        await db.delete(db_item)
        await db.commit()
        return True

class OrderInfoCRUD:
    """CRUD operations for OrderInfo model"""
    
    @staticmethod
    async def create(db: AsyncSession, info: OrderInfoCreate) -> OrderInfo:
        db_info = OrderInfo(**info.dict())
        db.add(db_info)
        await db.commit()
        await db.refresh(db_info)
        return db_info

    @staticmethod
    async def get(db: AsyncSession, info_id: int) -> Optional[OrderInfo]:
        result = await db.execute(select(OrderInfo).filter(OrderInfo.id == info_id))
        return result.scalars().first()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[OrderInfo]:
        result = await db.execute(select(OrderInfo))
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, info_id: int, info_update: OrderInfoUpdate) -> Optional[OrderInfo]:
        db_info = await OrderInfoCRUD.get(db, info_id)
        if not db_info:
            raise HTTPException(status_code=404, detail="Order info not found")
        
        for key, value in info_update.dict(exclude_unset=True).items():
            setattr(db_info, key, value)
        
        await db.commit()
        await db.refresh(db_info)
        return db_info

    @staticmethod
    async def delete(db: AsyncSession, info_id: int) -> bool:
        db_info = await OrderInfoCRUD.get(db, info_id)
        if not db_info:
            return False
        await db.delete(db_info)
        await db.commit()
        return True

class OrderCRUD:
    """CRUD operations for Order model"""
    
    @staticmethod
    async def create(db: AsyncSession, order: OrderCreate) -> Order:
        db_order = Order(**order.dict())
        db.add(db_order)
        await db.commit()
        await db.refresh(db_order)
        return db_order

    @staticmethod
    async def get(db: AsyncSession, order_id: int) -> Optional[Order]:
        result = await db.execute(
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.status_rel),
                selectinload(Order.info)
            )
            .filter(Order.id == order_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_all(
        db: AsyncSession, 
        user_id: Optional[UUID] = None, 
        session_id: Optional[UUID] = None,
        sort_by_id: Optional[str] = None,
        sort_by_price: Optional[str] = None,
        sort_by_date: Optional[str] = None,
    ) -> List[Order]:
        
        query = select(Order).options(
            selectinload(Order.items),
            selectinload(Order.status_rel),
            selectinload(Order.info)
        )
        if sort_by_id == "asc":
            query = query.order_by(Order.id.asc())
        elif sort_by_id == "desc":
            query = query.order_by(Order.id.desc())
        if sort_by_price == "asc":
            query = query.order_by(Order.total_price.asc())
        elif sort_by_price == "desc":
            query = query.order_by(Order.total_price.desc())
        if sort_by_date == "asc":
            query = query.order_by(Order.created_at.asc())
        elif sort_by_date == "desc":
            query = query.order_by(Order.created_at.desc())

        if user_id:
            query = query.filter(Order.user_id == user_id)
        if session_id:
            query = query.filter(Order.session_id == session_id)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
        db_order = await OrderCRUD.get(db, order_id)
        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        for key, value in order_update.dict(exclude_unset=True).items():
            setattr(db_order, key, value)
        
        await db.commit()
        await db.refresh(db_order)
        return db_order

    @staticmethod
    async def delete(db: AsyncSession, order_id: int) -> bool:
        db_order = await OrderCRUD.get(db, order_id)
        if not db_order:
            return False
        await db.delete(db_order)
        await db.commit()
        return True