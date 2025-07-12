from datetime import date, datetime, time
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from order.models import Order, OrderItem
from config.database import get_async_session
from leads.models import Lead, LeadStatus
from datetime import date, datetime, time
from sqlalchemy import and_, func, select
from catalog.models import Product
from user.models import User
from session.models import Session

router = APIRouter(prefix="/mini/report", tags=["mini"])

@router.get("/leads-by-status")
async def get_lead_status_report(
    start_date: date = Query(..., description="Дата начала (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Дата окончания (YYYY-MM-DD)"),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает количество лидов по каждому статусу за указанный период.
    """
    stmt = (
        select(LeadStatus.name, func.count(Lead.id))
        .join(Lead, Lead.status_id == LeadStatus.id, isouter=True)
        .where(
            Lead.created_at >= datetime.combine(start_date, time.min),
            Lead.created_at <= datetime.combine(end_date, time.max)
        )
        .group_by(LeadStatus.name)
        .order_by(LeadStatus.name)
    )

    result = await session.execute(stmt)
    data = result.all()

    return [
        {"status": name or "Без статуса", "lead_count": count}
        for name, count in data
    ]

@router.get("/report")
async def report_order(
    start_date: date = Query(..., description="Дата начала (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Дата окончания (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_async_session),
):
    # Маппинг поля сортировки
    sort_columns = {
        "date": func.date(Order.created_at),
        "orders_count": func.count(Order.id),
        "total_sum": func.sum(Order.total_price)
    }

    query = (
        select(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("orders_count"),
            func.sum(Order.total_price).label("total_sum")
        )
        .where(
            Order.status_id == 2,
            Order.created_at >= datetime.combine(start_date, datetime.min.time()),
            Order.created_at <= datetime.combine(end_date, datetime.max.time())
        )
        .group_by(func.date(Order.created_at))
    )

    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "date": row.date,
            "orders_count": row.orders_count,
            "total_sum": float(row.total_sum or 0)
        }
        for row in rows
    ]

@router.get("/top-products")
async def get_top_products(
    session: AsyncSession = Depends(get_async_session),
):
    """
    Топ-5 самых популярных товаров по количеству заказов за указанный период.
    """
    query = (
        select(
            Product.good_name.label("product_name"),
            func.sum(OrderItem.quantity).label("total_quantity")
        )
        .join(OrderItem, Product.good_id == OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(
            Order.status_id == 2,  # только завершённые заказы
        )
        .group_by(Product.good_name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
    )

    result = await session.execute(query)
    top_products = result.all()

    return [
        {"product_name": name, "total_quantity": int(quantity)}
        for name, quantity in top_products
    ]

@router.get("/clients")
async def get_clients_stats(db: AsyncSession = Depends(get_async_session),):
    # Кол-во зарегистрированных пользователей (клиентов), которые не суперадмины и имеют session_id
    registered_q = await db.execute(
        select(func.count(User.id))
        .where(
            and_(
                User.is_superuser != True,
                User.session_id.isnot(None)
            )
        )
    )
    registered_count = registered_q.scalar_one()

    # Кол-во сессий, которые не связаны с зарегистрированным пользователем
    # то есть session.session_id NOT IN (SELECT user.session_id)
    subquery = select(User.session_id).where(User.session_id.isnot(None))
    unregistered_q = await db.execute(
        select(func.count(Session.id))
        .where(Session.session_id.not_in(subquery))
    )
    unregistered_count = unregistered_q.scalar_one()

    return {
        "registered_clients": registered_count,
        "unregistered_clients": unregistered_count,
    }