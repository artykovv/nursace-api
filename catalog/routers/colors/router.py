from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session

from catalog.models import Color

router = APIRouter(prefix="/colors", tags=["colors"])

@router.get("/")
async def get_colors(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Color)
    result = await session.execute(query)

    colors = result.scalars().all()
    return colors

@router.get("/{color_id}")
async def get_color_by_id(
    color_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Color).where(Color.color_id == color_id)
    result = await session.execute(query)
    color = result.scalars().first()
    return color 