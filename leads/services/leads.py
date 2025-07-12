from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from leads.models import Lead, LeadProduct, LeadStatus
from leads.schemas.leads import LeadCreate, LeadUpdate, LeadProductCreate, LeadProductUpdate, LeadStatusCreate, LeadStatusUpdate
from sqlalchemy.orm import selectinload

class LeadCRUD:
    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(
            select(Lead)
            .options(
                selectinload(Lead.status),
                selectinload(Lead.products).selectinload(LeadProduct.product),
            )
        )
        leads = result.scalars().all()
        return leads

    @staticmethod
    async def get_by_id(session: AsyncSession, lead_id: int):
        result = await session.execute(
            select(Lead).where(Lead.id == lead_id)
            .options(
                selectinload(Lead.status),
                selectinload(Lead.products).selectinload(LeadProduct.product),
            )
        )
        lead = result.scalar_one_or_none()
        return lead

    @staticmethod
    async def create(session: AsyncSession, data: LeadCreate):
        lead = Lead(
            full_name=data.full_name,
            phone_number=data.phone_number,
            comment=data.comment,
            status_id=data.status_id,
        )
        session.add(lead)
        await session.commit()
        await session.refresh(lead)

        # Подгружаем связанные данные: status, products, product внутри LeadProduct
        result = await session.execute(
            select(Lead)
            .where(Lead.id == lead.id)
            .options(
                selectinload(Lead.status),
                selectinload(Lead.products).selectinload(LeadProduct.product)
            )
        )
        lead = result.scalar_one()

        return lead

    @staticmethod
    async def update(session: AsyncSession, lead_id: int, data: LeadUpdate):
        result = await session.execute(
            select(Lead).where(Lead.id == lead_id)
        )
        lead = result.scalar_one_or_none()
        if lead is None:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(lead, key, value)
        await session.commit()
        await session.refresh(lead)
        return lead

    @staticmethod
    async def delete(session: AsyncSession, lead_id: int):
        result = await session.execute(
            select(Lead).where(Lead.id == lead_id)
        )
        lead = result.scalar_one_or_none()
        if lead is None:
            return False
        await session.delete(lead)
        await session.commit()
        return True

class LeadProductCRUD:
    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(select(LeadProduct))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, product_id: int):
        result = await session.execute(
            select(LeadProduct).where(LeadProduct.id == product_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: LeadProductCreate):
        product = LeadProduct(**data.dict())
        session.add(product)
        await session.commit()
        await session.refresh(product)
        return product

    @staticmethod
    async def update(session: AsyncSession, product_id: int, data: LeadProductUpdate):
        result = await session.execute(
            select(LeadProduct).where(LeadProduct.id == product_id)
        )
        product = result.scalar_one_or_none()
        if product is None:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(product, key, value)
        await session.commit()
        await session.refresh(product)
        return product

    @staticmethod
    async def delete(session: AsyncSession, product_id: int):
        result = await session.execute(
            select(LeadProduct).where(LeadProduct.id == product_id)
        )
        product = result.scalar_one_or_none()
        if product is None:
            return False
        await session.delete(product)
        await session.commit()
        return True

class LeadStatusCRUD:
    @staticmethod
    async def get_all(session: AsyncSession):
        result = await session.execute(select(LeadStatus))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, status_id: int):
        result = await session.execute(
            select(LeadStatus).where(LeadStatus.id == status_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, data: LeadStatusCreate):
        status = LeadStatus(**data.dict())
        session.add(status)
        await session.commit()
        await session.refresh(status)
        return status

    @staticmethod
    async def update(session: AsyncSession, status_id: int, data: LeadStatusUpdate):
        result = await session.execute(
            select(LeadStatus).where(LeadStatus.id == status_id)
        )
        status = result.scalar_one_or_none()
        if status is None:
            return None
        for key, value in data.dict(exclude_unset=True).items():
            setattr(status, key, value)
        await session.commit()
        await session.refresh(status)
        return status

    @staticmethod
    async def delete(session: AsyncSession, status_id: int):
        result = await session.execute(
            select(LeadStatus).where(LeadStatus.id == status_id)
        )
        status = result.scalar_one_or_none()
        if status is None:
            return False
        await session.delete(status)
        await session.commit()
        return True