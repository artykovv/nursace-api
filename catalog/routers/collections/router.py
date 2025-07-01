from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session

from catalog.models import Collection, Product

router = APIRouter(prefix="/collections", tags=["collections"])

@router.get("/")
async def get_collections(
    session: AsyncSession = Depends(get_async_session)
):
    stmt = (
        select(Collection)
        .join(Product, Product.collection_id == Collection.collection_id)
        .where(Product.warehouse_quantity > 0)
        .distinct()
    )
    result = await session.execute(stmt)
    collections = result.scalars().all()
    return collections

@router.get("/{collection_id}")
async def get_collection_by_id(
    collection_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Collection).where(Collection.collection_id == collection_id)
    result = await session.execute(query)
    collection = result.scalars().first()
    return collection

