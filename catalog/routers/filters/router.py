from fastapi import APIRouter, Depends
from sqlalchemy import and_, distinct, select
from sqlalchemy.ext.asyncio import AsyncSession
from discounts.models.discounts import DiscountProduct, Discount
from config.database import get_async_session  
from catalog.models import Category, Product, Manufacturer, Collection, Color, Sex
from custom.models import CustomCategory

router = APIRouter(prefix="/filters", tags=["filters"])

@router.get("/")
async def get_available_filters(
    custom_category_id: int | None = None,
    category_id: int | None = None,
    manufacturer_id: int | None = None,
    collection_id: int | None = None,
    season_id: int | None = None,
    discounts: bool | None = None,
    discount_id: int | None = None,
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Product).where(Product.warehouse_quantity > 0)

    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    if manufacturer_id:
        stmt = stmt.where(Product.manufacturer_id == manufacturer_id)
    if collection_id:
        stmt = stmt.where(Product.collection_id == collection_id)
    if season_id:
        stmt = stmt.where(Product.season_id == season_id)
        
    # Скидки
    if discounts:
        stmt = stmt.where(
            Product.discounts.any(
                DiscountProduct.discount.has(Discount.is_active == True)
            )
        )
    if discount_id:
        stmt = stmt.where(
            Product.discounts.any(
                DiscountProduct.discount.has(
                    and_(Discount.is_active == True, Discount.id == discount_id)
                )
            )
        )
    if custom_category_id:
        stmt = stmt.where(
            Product.custom_categories.any(CustomCategory.category_id == custom_category_id)
        )

    subquery = stmt.subquery()

    # --- Цвета ---
    color_query = (
        select(distinct(Color.color_id).label("id"), Color.color_name.label("name"))
        .join(subquery, subquery.c.color_id == Color.color_id)
    )
    color_result = await session.execute(color_query)
    colors = [{"id": row.id, "name": row.name} for row in color_result]

    # --- Пол ---
    sex_query = (
        select(distinct(Sex.sex_id).label("id"), Sex.sex_name.label("name"))
        .join(subquery, subquery.c.sex_id == Sex.sex_id)
    )
    sex_result = await session.execute(sex_query)
    sexes = [{"id": row.id, "name": row.name} for row in sex_result]

    # --- Производители ---
    manufacturer_query = (
        select(distinct(Manufacturer.manufacturer_id).label("id"), Manufacturer.manufacturer_name.label("name"))
        .join(subquery, subquery.c.manufacturer_id == Manufacturer.manufacturer_id)
    )
    manufacturer_result = await session.execute(manufacturer_query)
    manufacturers = [{"id": row.id, "name": row.name} for row in manufacturer_result]

    # --- Коллекции ---
    collection_query = (
        select(distinct(Collection.collection_id).label("id"), Collection.collection_name.label("name"))
        .join(subquery, subquery.c.collection_id == Collection.collection_id)
    )
    collection_result = await session.execute(collection_query)
    collections = [{"id": row.id, "name": row.name} for row in collection_result]

    # --- Размеры ---
    size_query = select(distinct(subquery.c.product_size)).where(subquery.c.product_size.isnot(None))
    size_result = await session.execute(size_query)
    sizes = [{"value": row[0]} for row in size_result.all()]

    # --- Дочерние категории ---
    child_categories = []
    if category_id:
        child_category_query = select(Category).where(Category.parent_category_id == category_id)
        result = await session.execute(child_category_query)
        child_categories = [{"id": c.category_id, "name": c.category_name} for c in result.scalars().all()]

    return {
        "colors": colors,
        "sexes": sexes,
        "manufacturers": manufacturers,
        "collections": collections,
        "sizes": sizes,
        "child_categories": child_categories
    }