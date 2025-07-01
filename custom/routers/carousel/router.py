from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from custom.schemas.carousel import CarouselImageCreate, CarouselImageUpdate, CarouselImageRead
from custom.services.carousel import CarouselCRUD
from user.models import User
from user.auth.fastapi_users_instance import fastapi_users

router = APIRouter(prefix="/carousel", tags=["Carousel"])

@router.get("/", response_model=list[CarouselImageRead])
async def get_all(
    session: AsyncSession = Depends(get_async_session)
):
    return await CarouselCRUD.get_all(session)

@router.get("/{image_id}", response_model=CarouselImageRead)
async def get_one(
    image_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    image = await CarouselCRUD.get_by_id(session, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.post("/", response_model=CarouselImageRead)
async def create_image(
    data: CarouselImageCreate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await CarouselCRUD.create(session, data)

@router.put("/{image_id}", response_model=CarouselImageRead)
async def update_image(
    image_id: int, 
    data: CarouselImageUpdate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    updated = await CarouselCRUD.update(session, image_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Image not found")
    return updated

@router.delete("/{image_id}", status_code=204)
async def delete_image(
    image_id: int, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    deleted = await CarouselCRUD.delete(session, image_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Image not found")