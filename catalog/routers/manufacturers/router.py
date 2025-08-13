from sqlalchemy import select
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session

from catalog.models import Manufacturer, Product

router = APIRouter(prefix="/manufacturers", tags=["manufacturers"])

@router.get("/")
async def get_manufacturers(
    session: AsyncSession = Depends(get_async_session)
):
    stmt = (
        select(Manufacturer)
        .join(Product, Product.manufacturer_id == Manufacturer.manufacturer_id)
        .where(Product.warehouse_quantity > 0)
        .distinct()
    )
    result = await session.execute(stmt)
    manufacturers = result.scalars().all()
    return manufacturers

@router.get("/v3/")
async def get_manufacturers(
    session: AsyncSession = Depends(get_async_session)
):
    stmt = (
        select(Manufacturer)
        .join(Product, Product.manufacturer_id == Manufacturer.manufacturer_id)
        .where(Product.warehouse_quantity > 0,  Product.images.any())
        .distinct()
    )
    result = await session.execute(stmt)
    manufacturers = result.scalars().all()
    return manufacturers

@router.get("/{manufacturer_id}")
async def get_manufacturer_by_id(
    manufacturer_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Manufacturer).where(Manufacturer.manufacturer_id == manufacturer_id)
    result = await session.execute(query)
    manufacturer = result.scalars().first()
    return manufacturer

