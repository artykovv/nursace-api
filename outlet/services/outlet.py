from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, delete
from sqlalchemy.orm import selectinload

from catalog.models.products import Product
from outlet.models.outlets import Outlet, OutletProduct
from outlet.schemas.outlet import OutletCreate, OutletUpdate


class CRUDOutlet:

    @staticmethod
    async def create_outlet(session: AsyncSession, outlet_data: OutletCreate) -> Outlet:
        outlet = Outlet(**outlet_data.dict())
        session.add(outlet)
        await session.commit()
        await session.refresh(outlet)
        return outlet

    @staticmethod
    async def get_outlet_by_id(session: AsyncSession, outlet_id: int) -> Outlet | None:
        result = await session.execute(
            select(Outlet).where(Outlet.id == outlet_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_outlets(
        session: AsyncSession,
        is_active: Optional[bool]
    ) -> list[Outlet]:
        now = datetime.utcnow()

        if is_active is True:
            stmt = select(Outlet).where(
                and_(
                    Outlet.is_active == True,
                    Outlet.end_date > now
                )
            )
        elif is_active is False:
            stmt = select(Outlet).where(
                or_(
                    Outlet.is_active == False,
                    Outlet.end_date <= now
                )
            )
        else:
            stmt = select(Outlet)

        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_outlet(session: AsyncSession, outlet_id: int, data: OutletUpdate) -> Outlet | None:
        result = await session.execute(
            select(Outlet).where(Outlet.id == outlet_id).options(selectinload(Outlet.products))
        )
        outlet = result.scalar_one_or_none()
        if not outlet:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            setattr(outlet, key, value)

        # Пересчёт цен у связанных товаров
        related_product_ids = [op.product_id for op in outlet.products]
        for pid in related_product_ids:
            product = await session.get(Product, pid)
            if product and outlet.discount_percent is not None and product.retail_price is not None:
                discounted_price = product.retail_price * (1 - outlet.discount_percent / 100)
                product.retail_price_with_discount = round(discounted_price, 2)

        await session.commit()
        await session.refresh(outlet)
        return outlet

    @staticmethod
    async def delete_outlet(session: AsyncSession, outlet_id: int) -> bool:
        result = await session.execute(
            select(Outlet).where(Outlet.id == outlet_id).options(selectinload(Outlet.products))
        )
        outlet = result.scalar_one_or_none()
        if not outlet:
            return False

        related_product_ids = [op.product_id for op in outlet.products]

        await session.execute(
            delete(OutletProduct).where(OutletProduct.outlet_id == outlet_id)
        )

        for pid in related_product_ids:
            product = await session.get(Product, pid)
            if product:
                product.retail_price_with_discount = product.retail_price

        await session.delete(outlet)
        await session.commit()
        return True


class CRUDOutletProduct:
    @staticmethod
    async def add_products_to_outlet(session: AsyncSession, outlet_id: int, product_ids: list[int]):
        outlet = await session.get(Outlet, outlet_id)

        links = [
            OutletProduct(outlet_id=outlet_id, product_id=pid)
            for pid in product_ids
        ]
        session.add_all(links)

        for pid in product_ids:
            product = await session.get(Product, pid)
            if product and outlet and outlet.discount_percent is not None and product.retail_price is not None:
                discounted_price = product.retail_price * (1 - outlet.discount_percent / 100)
                product.retail_price_with_discount = round(discounted_price, 2)

        await session.commit()
        return links

    @staticmethod
    async def remove_products_from_outlet(session: AsyncSession, outlet_id: int, product_ids: list[int]):
        await session.execute(
            delete(OutletProduct).where(
                OutletProduct.outlet_id == outlet_id,
                OutletProduct.product_id.in_(product_ids)
            )
        )

        for pid in product_ids:
            product = await session.get(Product, pid)
            if product:
                product.retail_price_with_discount = product.retail_price

        await session.commit()
        return len(product_ids)

    @staticmethod
    async def get_products_by_outlet(session, outlet_id: int):
        result = await session.execute(
            select(Product)
            .join(OutletProduct, OutletProduct.product_id == Product.good_id)
            .where(OutletProduct.outlet_id == outlet_id)
            .options(selectinload(Product.images))  # чтобы не словить MissingGreenlet
        )
        return result.scalars().all()


