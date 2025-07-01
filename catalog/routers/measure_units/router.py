from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session

from catalog.models import MeasureUnit

router = APIRouter(prefix="/measure_units", tags=["measure_units"])

@router.get("/")
async def get_measure_units(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(MeasureUnit)
    result = await session.execute(query)

    measure_units = result.scalars().all()
    return measure_units

@router.get("/{measure_unit_id}")
async def get_measure_unit_by_id(
    measure_unit_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(MeasureUnit).where(MeasureUnit.measure_unit_id == measure_unit_id)
    result = await session.execute(query)
    measure_unit = result.scalars().first()
    return measure_unit

