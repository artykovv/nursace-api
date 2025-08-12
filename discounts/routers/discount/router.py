from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from catalog.schemas.product import BaseProductSchema
from discounts.schemas.discount import DiscountCreate, DiscountUpdate, DiscountInDB, ProductIDs
from discounts.services.discount import CRUDDiscount, CRUDDiscountProduct
from config.database import get_async_session

router = APIRouter(prefix="/discounts", tags=["Discounts"])


@router.post("/", response_model=DiscountInDB)
async def create_discount(
    discount_data: DiscountCreate,
    session: AsyncSession = Depends(get_async_session)
):
    return await CRUDDiscount.create_discount(session, discount_data)


@router.get("/", response_model=List[DiscountInDB])
async def list_all_discounts(is_active: Optional[bool] = Query(None), session: AsyncSession = Depends(get_async_session)):
    return await CRUDDiscount.get_discounts(session, is_active)


@router.get("/{discount_id}", response_model=DiscountInDB)
async def get_discount(discount_id: int, session: AsyncSession = Depends(get_async_session)):
    discount = await CRUDDiscount.get_discount_by_id(session, discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Скидка не найдена")
    return discount


@router.put("/{discount_id}", response_model=DiscountInDB)
async def update_discount(
    discount_id: int,
    discount_data: DiscountUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    updated = await CRUDDiscount.update_discount(session, discount_id, discount_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Скидка не найдена")
    return updated


@router.delete("/{discount_id}")
async def delete_discount(discount_id: int, session: AsyncSession = Depends(get_async_session)):
    success = await CRUDDiscount.delete_discount(session, discount_id)
    if not success:
        raise HTTPException(status_code=404, detail="Скидка не найдена")
    return {"detail": "Скидка удалена"}


@router.post("/{discount_id}/products")
async def add_products_to_discount(
    discount_id: int,
    products: ProductIDs,
    session: AsyncSession = Depends(get_async_session)
):
    discount = await CRUDDiscount.get_discount_by_id(session, discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Скидка не найдена")

    return await CRUDDiscountProduct.add_products_to_discount(
        session, discount_id, products.product_ids
    )


@router.delete("/{discount_id}/products")
async def remove_products_from_discount(
    discount_id: int,
    products: ProductIDs,
    session: AsyncSession = Depends(get_async_session)
):
    removed_count = await CRUDDiscountProduct.remove_products_from_discount(
        session, discount_id, products.product_ids
    )
    if removed_count == 0:
        raise HTTPException(status_code=404, detail="Связь скидки и товаров не найдена")

    return {"detail": f"Удалено товаров: {removed_count}"}

@router.get("/{discount_id}/products", response_model=List[BaseProductSchema])
async def get_products_by_discount(
    discount_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    discount = await CRUDDiscount.get_discount_by_id(session, discount_id)
    if not discount:
        raise HTTPException(status_code=404, detail="Скидка не найдена")

    products = await CRUDDiscountProduct.get_products_by_discount(session, discount_id)
    return products