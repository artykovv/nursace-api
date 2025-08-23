from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session

from catalog.models import Sex, Product

router = APIRouter(prefix="/sexes", tags=["sexes"])

@router.get("/")
async def get_sexes(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Sex)
    result = await session.execute(query)

    sexes = result.scalars().all()
    return sexes

@router.get("/v3/")
async def get_product_sexes(
    session: AsyncSession = Depends(get_async_session)
):
    stmt = (
        select(Sex)
        .join(Product, Product.sex_id == Sex.sex_id)
        .where(
            Product.warehouse_quantity > 0,
            Product.images.any()  # есть хотя бы одна картинка
        )
        .distinct()
    )
    result = await session.execute(stmt)
    seasons = result.scalars().all()
    return seasons

@router.get("/{sex_id}")
async def get_sex_by_id(
    sex_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Sex).where(Sex.sex_id == sex_id)
    result = await session.execute(query)
    sex = result.scalars().first()
    return sex

