from uuid import UUID
from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
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
from notification.tasks.email_sender import send_check_email
from catalog.models.products import Product

router = APIRouter(prefix="/orders", tags=["checkout"])

@router.post("/payment/check")
async def payment_check(request: Request, db: AsyncSession = Depends(get_async_session)):
    try:
        data = await request.json()
        pg_order_id = data.get("pg_order_id")
        pg_amount = data.get("pg_amount")

        if not pg_order_id or not pg_amount:
            return JSONResponse(
                content={"pg_status": "error", "pg_error_description": "Missing pg_order_id or pg_amount"},
                status_code=200
            )

        order = await db.get(Order, int(pg_order_id))
        if not order:
            return JSONResponse(
                content={"pg_status": "error", "pg_error_description": "Order not found"},
                status_code=200
            )

        if float(order.total_price) != float(pg_amount):
            return JSONResponse(
                content={"pg_status": "error", "pg_error_description": "Amount mismatch"},
                status_code=200
            )

        return JSONResponse(content={"pg_status": "ok"}, status_code=200)

    except Exception as e:
        print("Ошибка в payment_check:", e)
        return JSONResponse(
            content={"pg_status": "error", "pg_error_description": "Internal server error"},
            status_code=200
        )

class OrderRequest(BaseModel):
    order_id: int
    
@router.post("/test")
async def test_send_check_email(data: OrderRequest):
    task = await send_check_email(order_id=data.order_id)
    return task

@router.post("/payment/result")
async def payment_result(
    request: Request,
    db: AsyncSession = Depends(get_async_session),
    background_tasks: BackgroundTasks = None,
):
    # Заголовки запроса
    print("🔍 Headers:", dict(request.headers))

    # Сырое тело запроса
    body_bytes = await request.body()
    print("📦 Raw body:", body_bytes.decode("utf-8"))

    if not body_bytes:
        print("❗ Тело запроса пустое.")
        return {"status": "error", "message": "Empty body"}

    try:
        form = await request.form()
        data = dict(form)
        print("✅ Parsed form-data:", data)
    except Exception as e:
        print("❌ Ошибка при парсинге form-data:", str(e))
        return {"status": "error", "message": "Invalid form data"}

    order_id = data.get("pg_order_id")
    payment_id = data.get("pg_payment_id")
    amount = data.get("pg_amount")
    pg_result = data.get("pg_result")

    if not order_id or not payment_id:
        return {"status": "error", "message": "Missing order_id or payment_id"}

    order = await db.get(Order, int(order_id))
    if not order:
        return {"status": "error", "message": "Order not found"}

    if round(float(order.total_price), 2) != round(float(amount), 2):
        return {"status": "error", "message": "Amount mismatch"}

    if str(pg_result) == "1":
        status = await OrderStatusCRUD.get_by_name(name="paid", db=db)
        order.status_id = status.id
        background_tasks.add_task(send_check_email, int(order_id))
    else:
        # Если оплата не прошла, восстанавливаем количество товаров
        await restore_product_quantities(order_id, db)
        status = await OrderStatusCRUD.get_by_name(name="cancelled", db=db)
        order.status_id = status.id

    await db.commit()
    return {"status": "ok"}

async def restore_product_quantities(order_id: int, db: AsyncSession):
    """
    Восстанавливает количество товаров при отмене заказа.
    
    Эта функция используется в двух случаях:
    1. При неуспешной оплате (pg_result != "1")
    2. При ручной отмене заказа администратором
    
    Логика работы:
    1. Получает все позиции заказа с товарами
    2. Восстанавливает количество каждого товара
    3. Если товар снова появился в наличии, показывает его (display = 1)
    """
    # Получаем все позиции заказа с товарами
    stmt = select(OItem).where(OItem.order_id == order_id).options(selectinload(OItem.product))
    result = await db.execute(stmt)
    order_items = result.scalars().all()
    
    for item in order_items:
        product = item.product
        # Восстанавливаем количество товара на складе
        old_quantity = product.warehouse_quantity
        product.warehouse_quantity += item.quantity
        print(f"🔄 Восстановление товара {product.good_name}: {old_quantity} -> {product.warehouse_quantity}")
        
        # Если товар снова появился в наличии, показываем его
        if product.warehouse_quantity > 0 and product.display == 0:
            product.display = 1
            print(f"✅ Товар {product.good_name} снова показан (количество > 0)")

@router.post("/cancel/{order_id}")
async def cancel_order(order_id: int, db: AsyncSession = Depends(get_async_session)):
    """
    Отменяет заказ и восстанавливает количество товаров.
    
    Эта функция позволяет администраторам вручную отменять заказы.
    
    Ограничения:
    - Нельзя отменить уже оплаченный заказ
    - При отмене восстанавливается количество товаров на складе
    - Товары снова становятся видимыми, если их количество > 0
    
    Args:
        order_id: ID заказа для отмены
        
    Returns:
        dict: Статус операции и сообщение
    """
    # Получаем заказ
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(404, "Заказ не найден")
    
    # Проверяем, что заказ не оплачен
    paid_status = await OrderStatusCRUD.get_by_name(name="paid", db=db)
    if order.status_id == paid_status.id:
        raise HTTPException(400, "Нельзя отменить оплаченный заказ")
    
    # Восстанавливаем количество товаров
    await restore_product_quantities(order_id, db)
    
    # Устанавливаем статус "отменен"
    cancelled_status = await OrderStatusCRUD.get_by_name(name="cancelled", db=db)
    order.status_id = cancelled_status.id
    
    await db.commit()
    return {"status": "ok", "message": "Заказ отменен"}

@router.post("/checkout")
async def checkout(data: ChekoutOrderCreate, db: AsyncSession = Depends(get_async_session)):
    """
    Создает заказ из корзины пользователя.
    
    Логика работы:
    1. Проверяет корзину на наличие товаров
    2. Проверяет доступность товаров (display = 1)
    3. Проверяет достаточность количества товаров
    4. Проверяет минимальное количество для заказа
    5. Уменьшает количество товаров на складе
    6. Скрывает товары с нулевым количеством (display = 0)
    7. Создает заказ и позиции заказа
    8. Очищает корзину
    9. Генерирует ссылку для оплаты
    """
    if not (data.user_id or data.session_id):
        raise HTTPException(400, "Нужен либо user_id, либо session_id")

    # 1. Получаем корзину с загруженными товарами
    stmt = select(CartItem).where(
        CartItem.user_id == data.user_id if data.user_id else CartItem.session_id == data.session_id
    ).options(selectinload(CartItem.product))
    result = await db.execute(stmt)
    cart_items = result.scalars().all()
    if not cart_items:
        raise HTTPException(400, "Корзина пуста")

    # Проверяем, что все товары в корзине доступны для заказа
    for item in cart_items:
        if item.product.display == 0:
            raise HTTPException(400, f"Товар {item.product.good_name} недоступен для заказа")

    # 2. Проверяем наличие товаров и уменьшаем количество
    for item in cart_items:
        product = item.product
        
        # Проверка достаточности количества
        if product.warehouse_quantity < item.quantity:
            raise HTTPException(400, f"Недостаточно товара {product.good_name}. В наличии: {product.warehouse_quantity}, заказано: {item.quantity}")
        
        # Проверка минимального количества для заказа
        if product.min_quantity_for_order and item.quantity < product.min_quantity_for_order:
            raise HTTPException(400, f"Минимальное количество для заказа товара {product.good_name}: {product.min_quantity_for_order}")
        
        # Уменьшаем количество товара на складе
        old_quantity = product.warehouse_quantity
        product.warehouse_quantity -= item.quantity
        print(f"📦 Товар {product.good_name}: {old_quantity} -> {product.warehouse_quantity} (заказано: {item.quantity})")
        
        # Если товар закончился, скрываем его (display = 0)
        if product.warehouse_quantity == 0:
            product.display = 0
            print(f"🚫 Товар {product.good_name} скрыт (количество = 0)")

    # 3. Создаем информацию о заказе (OrderInfo)
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

    # 4. Рассчитываем общую сумму и создаём заказ (Order)
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

    # 5. Добавляем позиции заказа (OrderItem)
    for item in cart_items:
        oi = OItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.product.retail_price,
        )
        db.add(oi)

    # 6. Очистка корзины после создания заказа
    for item in cart_items:
        await db.delete(item)

    # Сохраняем все изменения в базе данных
    await db.commit()

    # 7. Формируем ссылку для оплаты
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