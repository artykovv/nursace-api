from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from outlet.schemas.outlet import OutletCreate, OutletUpdate, OutletInDB, ProductIDs
from outlet.services.outlet import CRUDOutlet, CRUDOutletProduct
from config.database import get_async_session
from catalog.schemas.product import BaseProductSchema

router = APIRouter(prefix="/outlets", tags=["Outlets"])


@router.post("/", response_model=OutletInDB)
async def create_outlet(
    outlet_data: OutletCreate,
    session: AsyncSession = Depends(get_async_session)
):
    return await CRUDOutlet.create_outlet(session, outlet_data)


@router.get("/", response_model=List[OutletInDB])
async def list_all_outlets(is_active: Optional[bool] = Query(None), session: AsyncSession = Depends(get_async_session)):
    return await CRUDOutlet.get_outlets(session, is_active)


@router.get("/{outlet_id}", response_model=OutletInDB)
async def get_outlet(outlet_id: int, session: AsyncSession = Depends(get_async_session)):
    outlet = await CRUDOutlet.get_outlet_by_id(session, outlet_id)
    if not outlet:
        raise HTTPException(status_code=404, detail="Аутлет не найден")
    return outlet


@router.put("/{outlet_id}", response_model=OutletInDB)
async def update_outlet(
    outlet_id: int,
    outlet_data: OutletUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    updated = await CRUDOutlet.update_outlet(session, outlet_id, outlet_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Аутлет не найден")
    return updated


@router.delete("/{outlet_id}")
async def delete_outlet(outlet_id: int, session: AsyncSession = Depends(get_async_session)):
    success = await CRUDOutlet.delete_outlet(session, outlet_id)
    if not success:
        raise HTTPException(status_code=404, detail="Аутлет не найден")
    return {"detail": "Аутлет удален"}


@router.post("/{outlet_id}/products")
async def add_products_to_outlet(
    outlet_id: int,
    products: ProductIDs,
    session: AsyncSession = Depends(get_async_session)
):
    outlet = await CRUDOutlet.get_outlet_by_id(session, outlet_id)
    if not outlet:
        raise HTTPException(status_code=404, detail="Аутлет не найден")

    return await CRUDOutletProduct.add_products_to_outlet(
        session, outlet_id, products.product_ids
    )


@router.delete("/{outlet_id}/products")
async def remove_products_from_outlet(
    outlet_id: int,
    products: ProductIDs,
    session: AsyncSession = Depends(get_async_session)
):
    removed_count = await CRUDOutletProduct.remove_products_from_outlet(
        session, outlet_id, products.product_ids
    )
    if removed_count == 0:
        raise HTTPException(status_code=404, detail="Связь аутлета и товаров не найдена")

    return {"detail": f"Удалено товаров: {removed_count}"}


@router.get("/{outlet_id}/products", response_model=List[BaseProductSchema])
async def get_products_by_outlet(
    outlet_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    outlet = await CRUDOutlet.get_outlet_by_id(session, outlet_id)
    if not outlet:
        raise HTTPException(status_code=404, detail="Аутлет не найден")

    products = await CRUDOutletProduct.get_products_by_outlet(session, outlet_id)
    return products


