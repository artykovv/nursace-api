from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, update, delete
from catalog.models.products import Product
from sqlalchemy.orm import selectinload
from discounts.models import Discount, DiscountProduct
from discounts.schemas.discount import DiscountCreate, DiscountUpdate



class CRUDDiscount:

    @staticmethod
    async def create_discount(session: AsyncSession, discount_data: DiscountCreate) -> Discount:
        discount = Discount(**discount_data.dict())
        session.add(discount)
        await session.commit()
        await session.refresh(discount)
        return discount

    @staticmethod
    async def get_discount_by_id(session: AsyncSession, discount_id: int) -> Discount | None:
        result = await session.execute(
            select(Discount).where(Discount.id == discount_id)
        )
        return result.scalar_one_or_none()

    
    @staticmethod
    async def get_discounts(
        session: AsyncSession,
        is_active: Optional[bool]
    ) -> list[Discount]:
        now = datetime.utcnow()

        if is_active is True:
            stmt = select(Discount).where(
                and_(
                    Discount.is_active == True,
                    Discount.end_date > now
                )
            )
        elif is_active is False:
            stmt = select(Discount).where(
                or_(
                    Discount.is_active == False,
                    Discount.end_date <= now
                )
            )
        else:  # is_active is None
            stmt = select(Discount)

        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_discount(session: AsyncSession, discount_id: int, data: DiscountUpdate) -> Discount | None:
        result = await session.execute(
            select(Discount).where(Discount.id == discount_id).options(selectinload(Discount.products))
        )
        discount = result.scalar_one_or_none()
        if not discount:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            setattr(discount, key, value)

        # Пересчёт цен у связанных товаров
        related_product_ids = [dp.product_id for dp in discount.products]
        for pid in related_product_ids:
            product = await session.get(Product, pid)
            if product:
                discounted_price = product.retail_price * (1 - discount.discount_percent / 100)
                product.retail_price_with_discount = round(discounted_price, 2)

        await session.commit()
        await session.refresh(discount)
        return discount

    @staticmethod
    async def delete_discount(session: AsyncSession, discount_id: int) -> bool:
        # Получаем скидку вместе с привязанными продуктами
        result = await session.execute(
            select(Discount).where(Discount.id == discount_id).options(selectinload(Discount.products))
        )
        discount = result.scalar_one_or_none()
        if not discount:
            return False

        # Получаем все связанные товары
        related_product_ids = [dp.product_id for dp in discount.products]

        # Удаляем связи
        await session.execute(
            delete(DiscountProduct).where(DiscountProduct.discount_id == discount_id)
        )

        # Обнуляем цену со скидкой у связанных товаров
        for pid in related_product_ids:
            product = await session.get(Product, pid)
            if product:
                product.retail_price_with_discount = product.retail_price

        # Удаляем саму скидку
        await session.delete(discount)
        await session.commit()
        return True

class CRUDDiscountProduct:
    @staticmethod
    async def add_products_to_discount(session: AsyncSession, discount_id: int, product_ids: list[int]):
        # Получаем саму скидку
        discount = await session.get(Discount, discount_id)

        # Добавляем связи
        links = [
            DiscountProduct(discount_id=discount_id, product_id=pid)
            for pid in product_ids
        ]
        session.add_all(links)

        # Обновляем товары
        for pid in product_ids:
            product = await session.get(Product, pid)
            if product and discount:
                discounted_price = product.retail_price * (1 - discount.discount_percent / 100)
                product.retail_price_with_discount = round(discounted_price, 2)

        await session.commit()
        return links

    @staticmethod
    async def remove_products_from_discount(session: AsyncSession, discount_id: int, product_ids: list[int]):
        # Удаляем связи
        await session.execute(
            delete(DiscountProduct).where(
                DiscountProduct.discount_id == discount_id,
                DiscountProduct.product_id.in_(product_ids)
            )
        )

        # Обнуляем цену со скидкой в товарах
        for pid in product_ids:
            product = await session.get(Product, pid)
            if product:
                product.retail_price_with_discount = product.retail_price

        await session.commit()
        return len(product_ids)
    
    @staticmethod
    async def get_products_by_discount(session: AsyncSession, discount_id: int):
        result = await session.execute(
            select(Product)
            .join(DiscountProduct, DiscountProduct.product_id == Product.good_id)
            .where(DiscountProduct.discount_id == discount_id)
            .options(selectinload(Product.images))  # если нужна подгрузка изображений
        )
        return result.scalars().all()