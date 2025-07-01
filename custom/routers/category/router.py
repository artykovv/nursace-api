from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from custom.schemas.custom_category import *
from custom.services.custom_category import CustomCategoryCRUD
from config.database import get_async_session  # или как у тебя называется
from user.models import User
from user.auth.fastapi_users_instance import fastapi_users
from catalog.schemas.product import BaseProductSchema

router = APIRouter(prefix="/custom-categories", tags=["Custom Categories"])

@router.post("/", response_model=CustomCategoryInDB)
async def create_category(
    data: CustomCategoryCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    return await CustomCategoryCRUD.create(session, data)


@router.get("/", response_model=list[CustomCategoryInDB])
async def list_categories(session: AsyncSession = Depends(get_async_session)):
    return await CustomCategoryCRUD.get_all(session)


@router.put("/{category_id}", response_model=CustomCategoryInDB)
async def update_category(
    category_id: int,
    data: CustomCategoryUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    category = await CustomCategoryCRUD.update(session, category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    success = await CustomCategoryCRUD.delete(session, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted"}


@router.post("/{category_id}/products/{product_id}")
async def add_product(
    category_id: int,
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    success = await CustomCategoryCRUD.add_product_to_category(session, product_id, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category or product not found")
    return {"message": "Product added to category"}


@router.delete("/{category_id}/products/{product_id}")
async def remove_product(
    category_id: int,
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    success = await CustomCategoryCRUD.remove_product_from_category(session, product_id, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category or product not found")
    return {"message": "Product removed from category"}

@router.get("/{category_id}/products", response_model=List[BaseProductSchema])
async def get_products_by_custom_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    products = await CustomCategoryCRUD.get_products_by_category(session, category_id)
    return products