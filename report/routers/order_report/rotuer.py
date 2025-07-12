from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from user.models import User
from user.auth.fastapi_users_instance import fastapi_users
from sqlalchemy.orm import selectinload

from order.models import Order

router = APIRouter(prefix="/report/order", tags=["report"])

@router.get("/details")
async def order_details_report(
    start_date: date = Query(..., description="Дата начала (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Дата окончания (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    query = (
        select(Order)
        .where(
            Order.status_id == 2,
            Order.created_at >= datetime.combine(start_date, datetime.min.time()),
            Order.created_at <= datetime.combine(end_date, datetime.max.time())
        )
        .options(
            selectinload(Order.info),         # подтягивает OrderInfo
            selectinload(Order.status_rel)    # если нужно, подтягивает статус
        )
        .order_by(Order.created_at.desc())
    )

    result = await db.execute(query)
    orders = result.scalars().all()

    return [
        {
            "order_id": order.id,
            "client": f"{order.info.first_name} {order.info.last_name}",
            "email": order.info.email,
            "total_price": float(order.total_price),
            "created_at": order.created_at.isoformat()
        }
        for order in orders
    ]