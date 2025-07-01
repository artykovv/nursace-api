from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from custom.models import CarouselImage
from custom.schemas.carousel import CarouselImageCreate, CarouselImageUpdate

class CarouselCRUD:
    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(select(CarouselImage))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, image_id: int):
        result = await session.execute(
            select(CarouselImage).where(CarouselImage.id == image_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: CarouselImageCreate):
        image = CarouselImage(**data.dict())
        session.add(image)
        await session.commit()
        await session.refresh(image)
        return image

    @staticmethod
    async def update(session: AsyncSession, image_id: int, data: CarouselImageUpdate):
        result = await session.execute(
            select(CarouselImage).where(CarouselImage.id == image_id)
        )
        image = result.scalar_one_or_none()
        if image is None:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(image, key, value)
        await session.commit()
        await session.refresh(image)
        return image

    @staticmethod
    async def delete(session: AsyncSession, image_id: int):
        result = await session.execute(
            select(CarouselImage).where(CarouselImage.id == image_id)
        )
        image = result.scalar_one_or_none()
        if image is None:
            return False
        await session.delete(image)
        await session.commit()
        return True