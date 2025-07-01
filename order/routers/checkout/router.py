from uuid import UUID
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from payment.freedompay.generate_freedompay_link import generate_freedompay_link
from config.database import get_async_session
from sqlalchemy.orm import selectinload
from order.models import (
    OrderInfo, Order, OrderItem as OItem
)
from cart.models import CartItem
from order.services.order import OrderStatusCRUD
from order.schemas.order import ChekoutOrderCreate

router = APIRouter(prefix="/orders", tags=["checkout"])

@router.post("/payment/check")
async def payment_check(pg_order_id: str, pg_amount: str, db: AsyncSession = Depends(get_async_session)):
    order = await db.get(Order, int(pg_order_id))
    if not order or float(order.total_price) != float(pg_amount):
        return {"pg_status": "error", "pg_error_description": "Order not found or amount mismatch"}
    return {"pg_status": "ok"}

@router.post("/payment/result")
async def payment_result(payload: dict = Body(...), db: AsyncSession = Depends(get_async_session)):
    # Проверить подпись pg_sig, рекомендую парсинг и верификацию
    order_id = int(payload["pg_order_id"])
    status = payload.get("pg_status")  # обычно "ok" или "error"

    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    if status == "ok":
        order.status_id = await OrderStatusCRUD.get_by_name(name="paid", db=db)
    else:
        order.status_id = await OrderStatusCRUD.get_by_name(name="cancelled", db=db)

    await db.commit()
    return {"status": "ok"}  # обязательно



@router.post("/checkout")
async def checkout(data: ChekoutOrderCreate, db: AsyncSession = Depends(get_async_session)):
    if not (data.user_id or data.session_id):
        raise HTTPException(400, "Нужен либо user_id, либо session_id")

    # 1. Получаем корзину
    stmt = select(CartItem).where(
        CartItem.user_id == data.user_id if data.user_id else CartItem.session_id == data.session_id
    ).options(selectinload(CartItem.product))
    result = await db.execute(stmt)
    cart_items = result.scalars().all()
    if not cart_items:
        raise HTTPException(400, "Корзина пуста")

    # 2. Создаем OrderInfo
    info = OrderInfo(
        # Assign user_id if provided
        user_id=data.user_id if data.is_save and data.user_id else None,
        session_id=data.session_id if data.is_save and data.session_id else None,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        address_line1=data.address_line1,
        city=data.city,
        region=data.region,
        postal_code=data.postal_code,
        phone=data.phone,
        order_note=data.order_note,
    )
    db.add(info)
    await db.flush()

    # 3. Рассчитываем сумму и создаём Order
    total = sum(item.product.retail_price * item.quantity for item in cart_items)

    order = Order(
        user_id=data.user_id,
        session_id=data.session_id,
        info_id=info.id,
        total_price=total,
        status_id=1  # статус "new"
    )
    db.add(order)
    await db.flush()

    # 4. Добавляем позиции OrderItem
    for item in cart_items:
        oi = OItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.retail_price,
        )
        db.add(oi)

    # 5. Очистка корзины
    for item in cart_items:
        await db.delete(item)

    await db.commit()

    # 6. Формируем payment_url (пример)
    payment_url = await generate_freedompay_link(
        order.id, 
        float(order.total_price), 
        description=f"Order #{order.id}", 
        user_phone=data.phone, 
        user_email=data.email
    )

    return {"order_id": order.id, "payment_url": payment_url}

@router.get("/last_order_info/")
async def get_last_order_info(user_id: UUID, db: AsyncSession = Depends(get_async_session)):
    stmt = select(OrderInfo).where(OrderInfo.user_id == user_id).order_by(OrderInfo.created_at.desc()).limit(1)
    result = await db.execute(stmt)
    order_info = result.scalars().first()
    if not order_info:
        raise HTTPException(status_code=404, detail="No order info found for user")
    return {
        "first_name": order_info.first_name,
        "last_name": order_info.last_name,
        "address_line1": order_info.address_line1,
        "city": order_info.city,
        "region": order_info.region,
        "postal_code": order_info.postal_code,
        "phone": order_info.phone,
        "email": order_info.email or "",
        "order_note": order_info.order_note or ""
    }