from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session

from catalog.models import Material

router = APIRouter(prefix="/materials", tags=["materials"])

@router.get("/")
async def get_materials(
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Material)
    result = await session.execute(query)

    materials = result.scalars().all()
    return materials

@router.get("/{material_id}")
async def get_material_by_id(
    material_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Material).where(Material.material_id == material_id)
    result = await session.execute(query)
    material = result.scalars().first()
    return material

