from fastapi import APIRouter, Depends
from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session

from catalog.models import Category, Product

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/")
async def get_categories(
    session: AsyncSession = Depends(get_async_session)
):
    stmt = (
        select(Category)
        .join(Product, Product.category_id == Category.category_id)
        .where(Product.warehouse_quantity > 0)
        .distinct()
    )
    result = await session.execute(stmt)
    categories = result.scalars().all()
    return categories

@router.get("/v3/")
async def get_categories(
    session: AsyncSession = Depends(get_async_session)
):
    stmt = (
        select(Category)
        .join(Product, Product.category_id == Category.category_id)
        .where(
            Product.warehouse_quantity > 0,
            Product.images.any()  # только категории с товарами, у которых есть фото
        )
        .distinct()
    )
    result = await session.execute(stmt)
    categories = result.scalars().all()
    return categories

@router.get("/{category_id}")
async def get_category_by_id(
    category_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Category).where(Category.category_id == category_id)
    result = await session.execute(query)
    category = result.scalars().first()
    return category

