from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from sqlalchemy.orm import selectinload, aliased
from user.models import User
from user.auth.fastapi_users_instance import fastapi_users


from catalog.services.products import ProductServices
from catalog.schemas.product import BaseProductSchema, UpdateProductSchema, SimilarProductSchema, UpdateProductImageSchema

from catalog.models import Product, Collection, Category, ProductImage

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/v1/", response_model=List[BaseProductSchema])
async def get_products_by_filters(
    category_id: Optional[List[int]] = Query(None),
    manufacturer_id: Optional[List[int]] = Query(None),
    collection_id: Optional[List[int]] = Query(None),
    season_id: Optional[int] = None,
    sex_id: Optional[List[int]] = Query(None),
    color_id: Optional[List[int]] = Query(None),
    material_id: Optional[int] = None,
    measure_unit_id: Optional[int] = None,
    guarantee_mes_unit_id: Optional[int] = None,
    model_good_id: Optional[int] = None,
    product_size: Optional[List[int]] = Query(None),
    sort_by_name: Optional[str] = Query(None, regex="^(asc|desc)$"),
    sort_by_id: Optional[str] = Query(None, regex="^(asc|desc)$"),
    sort_by_price: Optional[str] = Query(None, regex="^(asc|desc)$"),
    price_gt: Optional[float] = None,
    price_lt: Optional[float] = None,
    search: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
):
    # Подзапрос с ранжированием товаров по артикулам
    ranked_subq = (
        select(
            Product.good_id,
            func.row_number().over(
                partition_by=Product.articul,
                order_by=[Product.retail_price_with_discount.asc(), Product.good_id.asc()]
            ).label("rank")
        )
        .where(Product.warehouse_quantity > 0)
        .subquery()
    )

    # Подзапрос с good_id товаров с rank=1 (минимальная цена и минимальный good_id)
    min_good_ids_subq = select(ranked_subq.c.good_id).where(ranked_subq.c.rank == 1).subquery()

    # Основной запрос — выбираем товары с good_id из подзапроса
    query = select(Product).where(Product.good_id.in_(select(min_good_ids_subq)))

    # Применяем фильтры

    # Рекурсивный фильтр по коллекциям
    if collection_id:
        collection_cte = (
            select(Collection.collection_id)
            .where(Collection.collection_id.in_(collection_id))
            .cte(name="collection_tree", recursive=True)
        )
        collection_alias = aliased(Collection)
        collection_cte = collection_cte.union_all(
            select(collection_alias.collection_id)
            .where(collection_alias.parent_collection_id == collection_cte.c.collection_id)
        )
        query = query.where(Product.collection_id.in_(select(collection_cte.c.collection_id)))

    # Рекурсивный фильтр по категориям
    if category_id:
        category_cte = (
            select(Category.category_id)
            .where(Category.category_id.in_(category_id))
            .cte(name="category_cte", recursive=True)
        )
        category_alias = aliased(Category)
        category_cte = category_cte.union_all(
            select(category_alias.category_id)
            .where(category_alias.parent_category_id == category_cte.c.category_id)
        )
        query = query.where(Product.category_id.in_(select(category_cte.c.category_id)))

    # Простые фильтры
    if manufacturer_id:
        query = query.where(Product.manufacturer_id.in_(manufacturer_id))
    if season_id is not None:
        query = query.where(Product.season_id == season_id)
    if sex_id:
        query = query.where(Product.sex_id.in_(sex_id))
    if color_id:
        query = query.where(Product.color_id.in_(color_id))
    if material_id:
        query = query.where(Product.material_id == material_id)
    if measure_unit_id:
        query = query.where(Product.measure_unit_id == measure_unit_id)
    if guarantee_mes_unit_id:
        query = query.where(Product.guarantee_mes_unit_id == guarantee_mes_unit_id)
    if model_good_id:
        query = query.where(Product.model_good_id == model_good_id)
    if product_size:
        query = query.where(Product.product_size.in_(product_size))

    if price_gt is not None:
        query = query.where(Product.retail_price_with_discount >= price_gt)
    if price_lt is not None:
        query = query.where(Product.retail_price_with_discount <= price_lt)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Product.good_name.ilike(search_term),
                Product.articul.ilike(search_term),
            )
        )

    # Добавляем подгрузку изображений
    query = query.options(selectinload(Product.images))

    # Сортировки
    if sort_by_name == "asc":
        query = query.order_by(Product.good_name.asc())
    elif sort_by_name == "desc":
        query = query.order_by(Product.good_name.desc())

    if sort_by_id == "asc":
        query = query.order_by(Product.good_id.asc())
    elif sort_by_id == "desc":
        query = query.order_by(Product.good_id.desc())

    if sort_by_price == "asc":
        query = query.order_by(Product.retail_price_with_discount.asc())
    elif sort_by_price == "desc":
        query = query.order_by(Product.retail_price_with_discount.desc())

    result = await session.execute(query)
    products = result.scalars().unique().all()

    return products

@router.get("/", response_model=List[BaseProductSchema])
async def get_products_by_filters(
    category_id: Optional[List[int]] = Query(None),
    manufacturer_id: Optional[List[int]] = Query(None),
    collection_id: Optional[List[int]] = Query(None),
    season_id: Optional[int] = None,
    sex_id: Optional[List[int]] = Query(None),
    color_id: Optional[List[int]] = Query(None),
    material_id: Optional[int] = None,
    measure_unit_id: Optional[int] = None,
    guarantee_mes_unit_id: Optional[int] = None,
    model_good_id: Optional[int] = None,
    product_size: Optional[List[int]] = Query(None),
    sort_by_name: Optional[str] = Query(None, regex="^(asc|desc)$"),
    sort_by_id: Optional[str] = Query(None, regex="^(asc|desc)$"),
    sort_by_price: Optional[str] = Query(None, regex="^(asc|desc)$"),
    price_gt: Optional[float] = None,
    price_lt: Optional[float] = None,
    search: Optional[str] = None,
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Product).where(Product.warehouse_quantity > 0)

    # Рекурсивные фильтры по коллекциям
    if collection_id:
        collection_cte = (
            select(Collection.collection_id)
            .where(Collection.collection_id.in_(collection_id))
            .cte(name="collection_tree", recursive=True)
        )
        collection_alias = aliased(Collection)
        collection_cte = collection_cte.union_all(
            select(collection_alias.collection_id)
            .where(collection_alias.parent_collection_id == collection_cte.c.collection_id)
        )
        query = query.where(Product.collection_id.in_(select(collection_cte.c.collection_id)))

    # Рекурсивные фильтры по категориям
    if category_id:
        category_cte = (
            select(Category.category_id)
            .where(Category.category_id.in_(category_id))
            .cte(name="category_cte", recursive=True)
        )
        category_alias = aliased(Category)
        category_cte = category_cte.union_all(
            select(category_alias.category_id)
            .where(category_alias.parent_category_id == category_cte.c.category_id)
        )
        query = query.where(Product.category_id.in_(select(category_cte.c.category_id)))

    # Остальные фильтры
    if manufacturer_id:
        query = query.where(Product.manufacturer_id.in_(manufacturer_id))
    if season_id is not None:
        query = query.where(Product.season_id == season_id)
    if sex_id:
        query = query.where(Product.sex_id.in_(sex_id))
    if color_id:
        query = query.where(Product.color_id.in_(color_id))
    if material_id:
        query = query.where(Product.material_id == material_id)
    if measure_unit_id:
        query = query.where(Product.measure_unit_id == measure_unit_id)
    if guarantee_mes_unit_id:
        query = query.where(Product.guarantee_mes_unit_id == guarantee_mes_unit_id)
    if model_good_id:
        query = query.where(Product.model_good_id == model_good_id)
    if product_size:
        query = query.where(Product.product_size.in_(product_size))

    if price_gt is not None:
        query = query.where(Product.retail_price_with_discount >= price_gt)
    if price_lt is not None:
        query = query.where(Product.retail_price_with_discount <= price_lt)

    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Product.good_name.ilike(search_term),
                Product.articul.ilike(search_term),
            )
        )

    # Подгрузка изображений
    query = query.options(selectinload(Product.images))

    # Сортировка
    if sort_by_name == "asc":
        query = query.order_by(Product.good_name.asc())
    elif sort_by_name == "desc":
        query = query.order_by(Product.good_name.desc())

    if sort_by_id == "asc":
        query = query.order_by(Product.good_id.asc())
    elif sort_by_id == "desc":
        query = query.order_by(Product.good_id.desc())

    if sort_by_price == "asc":
        query = query.order_by(Product.retail_price_with_discount.asc())
    elif sort_by_price == "desc":
        query = query.order_by(Product.retail_price_with_discount.desc())

    result = await session.execute(query)
    products = result.scalars().unique().all()

    return products

@router.get("/{product_id}", response_model=BaseProductSchema)
async def product_by_id(product_id: int, session: AsyncSession = Depends(get_async_session)):
    product = await ProductServices.get_product_by_id(session, product_id)
    return product

@router.put("/{product_id}", response_model=UpdateProductSchema)
async def update_product(
    product_id: int, 
    product_data: UpdateProductSchema, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    print(product_data)
    product = await ProductServices.update_product(session, product_id, product_data)
    return product

@router.put("/{product_id}/images", response_model=BaseProductSchema)
async def update_product_images(
    product_id: int, 
    images: List[UpdateProductImageSchema], 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    product = await ProductServices.update_product_images(session, product_id, images)
    return product


@router.get("/{product_id}/similar", response_model=list[SimilarProductSchema])
async def get_similar_products(
    product_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Product)
        .options(selectinload(Product.color))
        .where(Product.good_id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product or not product.articul:
        return []

    query = (
        select(Product)
        .options(selectinload(Product.color))
        .where(
            Product.good_id != product.good_id,
            Product.articul == product.articul,
            or_(
                Product.color_id != product.color_id,
                Product.product_size != product.product_size
            )
        )
    )

    result = await session.execute(query)
    similar_products = result.scalars().all()
    all_products = [product] + similar_products
    all_products_sorted = sorted(all_products, key=lambda p: p.good_id)

    return all_products_sorted

@router.delete("/{product_id}/images", status_code=204)
async def delete_product_images(
    product_id: int,
    image_ids: List[int],
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    result = await session.execute(
        select(Product).options(selectinload(Product.images)).where(Product.good_id == product_id)
    )
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Проверим, что картинки действительно принадлежат этому товару
    product_image_ids = {image.image_id for image in product.images}
    invalid_ids = set(image_ids) - product_image_ids
    if invalid_ids:
        raise HTTPException(status_code=400, detail=f"Images not found in product: {list(invalid_ids)}")

    # Удаляем изображения
    await session.execute(
        delete(ProductImage).where(ProductImage.image_id.in_(image_ids))
    )
    await session.commit()
    return None  # HTTP 204