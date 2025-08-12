from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from sqlalchemy.orm import selectinload

from catalog.models import Color
from catalog.schemas.color import ColorCreate, ColorUpdate

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

@router.post("/", status_code=201)
async def create_color(
    data: ColorCreate,
    session: AsyncSession = Depends(get_async_session)
):
    new_color = Color(**data.dict())
    session.add(new_color)
    await session.commit()
    await session.refresh(new_color)
    return new_color

@router.delete("/{color_id}")
async def delete_color(
    color_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    query = (
        select(Color)
        .options(selectinload(Color.products))  # заранее подгружаем products
        .where(Color.color_id == color_id)
    )
    result = await session.execute(query)
    color = result.scalars().first()

    if not color:
        raise HTTPException(status_code=404, detail="Color not found")

    if color.products:  # теперь безопасно
        raise HTTPException(
            status_code=400,
            detail="Cannot delete color with linked products"
        )

    await session.delete(color)
    await session.commit()
    return {"detail": "Color deleted successfully"}

@router.patch("/{color_id}")
async def update_color(
    color_id: int,
    data: ColorUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    query = select(Color).where(Color.color_id == color_id)
    result = await session.execute(query)
    color = result.scalars().first()

    if not color:
        raise HTTPException(status_code=404, detail="Color not found")

    for key, value in data.dict(exclude_unset=True).items():
        setattr(color, key, value)

    await session.commit()
    await session.refresh(color)
    return color