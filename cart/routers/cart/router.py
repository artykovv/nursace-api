from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from config.database import get_async_session
from catalog.models import Product
from cart.models.cart import CartItem
from cart.schemas.cart import CartItemCreate, CartItemResponse
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/cart", tags=["Cart"])

# Добавить в корзину
@router.post("/")
async def add_to_cart(
    item: CartItemCreate, 
    db: AsyncSession = Depends(get_async_session)
):

    # Проверим, что товар существует
    product = await db.get(Product, item.product_id)
    if not product or product.warehouse_quantity == 0:
        raise HTTPException(status_code=404, detail="Product not found or out of stock")

    # Добавим или обновим количество
    stmt = select(CartItem).where(
        CartItem.product_id == item.product_id,
        (CartItem.session_id == item.session_id) if item.session_id else (CartItem.user_id == item.user_id)
    )
    result = await db.execute(stmt)
    cart_item = result.scalars().first()

    if cart_item:
        cart_item.quantity += item.quantity
    else:
        cart_item = CartItem(**item.dict())

    db.add(cart_item)
    await db.commit()
    await db.refresh(cart_item)
    return cart_item

@router.post("/v2")
async def add_to_cart_v2(
    item: CartItemCreate,
    db: AsyncSession = Depends(get_async_session)
):
    # Проверим наличие товара
    product = await db.get(Product, item.product_id)
    if not product or product.warehouse_quantity == 0:
        raise HTTPException(status_code=404, detail="Product not found or out of stock")

    # Подготовим словарь для вставки
    insert_data = item.dict()

    # Конфликт по product + session или product + user
    conflict_cols = ['product_id', 'session_id'] if item.session_id else ['product_id', 'user_id']

    stmt = (
        insert(CartItem)
        .values(**insert_data)
        .on_conflict_do_update(
            index_elements=conflict_cols,
            set_={"quantity": CartItem.quantity + item.quantity}
        )
        .returning(CartItem.id, CartItem.product_id, CartItem.quantity)
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.fetchone()._asdict()

# Получить корзину
@router.get("/", response_model=list[CartItemResponse])
async def get_cart(
    session_id: UUID | None = None, 
    user_id: UUID | None = None, 
    db: AsyncSession = Depends(get_async_session)
):
    stmt = select(CartItem).where(
        (CartItem.session_id == session_id) if session_id else (CartItem.user_id == user_id)
    ).options(
        selectinload(CartItem.product).selectinload(Product.images)
    ).order_by(CartItem.id.asc())
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/count")
async def get_cart_count(
    session_id: UUID | None = None,
    user_id: UUID | None = None,
    db: AsyncSession = Depends(get_async_session)
):
    if not session_id and not user_id:
        raise HTTPException(status_code=400, detail="Either session_id or user_id must be provided")

    stmt = select(func.count()).select_from(CartItem).where(
        CartItem.session_id == session_id if session_id else CartItem.user_id == user_id
    )

    result = await db.execute(stmt)
    count = result.scalar() or 0
    return {"count": count}


@router.put("/update-count")
async def update_quantity_by_session(
    product_id: int,
    new_quantity: int,
    session_id: UUID | None = None, 
    user_id: UUID | None = None, 
    db: AsyncSession = Depends(get_async_session),
):
    if new_quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")

    if not user_id and not session_id:
        raise HTTPException(status_code=400, detail="Either user_id or session_id must be provided")

    condition = (
        (CartItem.user_id == user_id) if user_id else (CartItem.session_id == session_id)
    )

    stmt = (
        update(CartItem)
        .where(condition, CartItem.product_id == product_id)
        .values(quantity=new_quantity)
        .execution_options(synchronize_session="fetch")
    )
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Cart item not found")

    return {"message": "Quantity updated"}

# Удалить из корзины
@router.delete("/remove", status_code=204)
async def delete_cart_item_by_session_and_product(
    product_id: int,
    session_id: UUID | None = None, 
    user_id: UUID | None = None, 
    db: AsyncSession = Depends(get_async_session)
):
    if not user_id and not session_id:
        raise HTTPException(status_code=400, detail="Either user_id or session_id must be provided")

    condition = (
        (CartItem.user_id == user_id) if user_id else (CartItem.session_id == session_id)
    )

    stmt = select(CartItem).where(
        condition,
        CartItem.product_id == product_id
    )

    result = await db.execute(stmt)
    cart_item = result.scalar_one_or_none()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found")

    await db.delete(cart_item)
    await db.commit()