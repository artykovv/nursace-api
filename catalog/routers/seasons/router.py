from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session

from catalog.models import Season, Product

router = APIRouter(prefix="/seasons", tags=["seasons"])

@router.get("/")
async def get_seasons(
    session: AsyncSession = Depends(get_async_session)
):
    stmt = (
        select(Season)
        .join(Product, Product.season_id == Season.season_id)
        .distinct()
    )
    result = await session.execute(stmt)
    seasons = result.scalars().all()
    return seasons

@router.get("/{season_id}")
async def get_season_by_id(
    season_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Season).where(Season.season_id == season_id)
    result = await session.execute(query)
    season = result.scalars().first()
    return season

