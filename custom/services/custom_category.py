from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from catalog.models import Product
from custom.models import CustomCategory, product_custom_category
from custom.schemas.custom_category import CustomCategoryCreate, CustomCategoryUpdate
from sqlalchemy.orm import selectinload


class CustomCategoryCRUD:
    @staticmethod
    async def create(session: AsyncSession, data: CustomCategoryCreate) -> CustomCategory:
        category = CustomCategory(**data.dict())
        session.add(category)
        await session.commit()
        await session.refresh(category)
        return category

    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(select(CustomCategory))
        return result.scalars().all()

    @staticmethod
    async def get(session: AsyncSession, category_id: int) -> CustomCategory | None:
        return await session.get(CustomCategory, category_id)

    @staticmethod
    async def update(session: AsyncSession, category_id: int, data: CustomCategoryUpdate):
        category = await session.get(CustomCategory, category_id)
        if not category:
            return None
        for key, value in data.dict().items():
            setattr(category, key, value)
        await session.commit()
        await session.refresh(category)
        return category

    @staticmethod
    async def delete(session: AsyncSession, category_id: int):
        category = await session.get(CustomCategory, category_id)
        if not category:
            return False
        await session.delete(category)
        await session.commit()
        return True

    @staticmethod
    async def add_product_to_category(session: AsyncSession, product_id: int, category_id: int):
        result = await session.execute(
            select(CustomCategory)
            .options(selectinload(CustomCategory.products))
            .where(CustomCategory.category_id == category_id)
        )
        category = result.scalar_one_or_none()

        result = await session.execute(
            select(Product).where(Product.good_id == product_id)
        )
        product = result.scalar_one_or_none()

        if not category or not product:
            return False

        category.products.append(product)
        await session.commit()
        return True

    @staticmethod
    async def remove_product_from_category(session: AsyncSession, product_id: int, category_id: int):
        category = await session.get(CustomCategory, category_id)
        product = await session.get(Product, product_id)
        if not category or not product:
            return False
        if product in category.products:
            category.products.remove(product)
            await session.commit()
        return True
    
    @staticmethod
    async def get_products_by_category(session: AsyncSession, category_id: int):
        result = await session.execute(
            select(CustomCategory)
            .options(
                selectinload(CustomCategory.products).selectinload(Product.images)
            )
            .where(CustomCategory.category_id == category_id)
        )
        category = result.scalar_one_or_none()
        if not category:
            return []
        return category.products