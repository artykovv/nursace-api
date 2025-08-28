from typing import List
from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from catalog.models import Product
from catalog.models.product_images import ProductImage
from catalog.schemas.product import ProductImageSchema, UpdateProductSchema, UpdateProductImageSchema

class ProductServices:

    async def get_product_by_id(session, product_id: int):
        result = await session.execute(
            select(Product).options(selectinload(Product.images)).where(Product.good_id == product_id)
        )
        db_product = result.scalar_one_or_none()
        return db_product
    
    async def update_product(session: AsyncSession, product_id: int, product_data: UpdateProductSchema):
        db_product = await session.get(Product, product_id)
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        update_data = product_data.dict(exclude_unset=True)
        # Определяем, нужно ли распространять изменение цвета на товары с тем же артикулом
        propagate_color_change = 'color_id' in update_data
        new_color_id = update_data.get('color_id') if propagate_color_change else None
        for key, value in update_data.items():
            setattr(db_product, key, value)

        # Если изменился цвет, находим все товары с тем же артикулом и обновляем им color_id
        if propagate_color_change:
            current_articul = db_product.articul  # после применения возможного изменения артикула
            similar_products_result = await session.execute(
                select(Product).where(Product.articul == current_articul)
            )
            similar_products = similar_products_result.scalars().all()

            for similar_product in similar_products:
                if similar_product.good_id != product_id:
                    similar_product.color_id = new_color_id

        try:
            await session.commit()
            await session.refresh(db_product)
            return db_product
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=f"Error updating product: {str(e)}")
    
    async def update_product_images(session: AsyncSession, product_id: int, images: List[UpdateProductImageSchema]):
        # Найти исходный товар
        result = await session.execute(
            select(Product).options(selectinload(Product.images)).where(Product.good_id == product_id)
        )
        db_product = result.scalar_one_or_none()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Получаем все товары с тем же артикулом (включая текущий)
        current_articul = db_product.articul
        similar_products_result = await session.execute(
            select(Product).options(selectinload(Product.images)).where(Product.articul == current_articul)
        )
        similar_products = similar_products_result.scalars().all()

        # Нормализуем входные изображения: убираем дубликаты по URL, назначаем порядковые номера,
        # и выставляем главный только для первого (order == 0)
        seen_urls = set()
        normalized = []
        for idx, image in enumerate(images):
            url = image.image_url
            if url in seen_urls:
                continue
            seen_urls.add(url)
            order_value = image.order if image.order is not None else len(normalized)
            normalized.append({
                "image_url": url,
                "order": order_value,
                # Главным делаем только первый по порядку, независимо от входного is_main
                "is_main": False,
            })

        # Убедимся, что хотя бы одно изображение есть
        if not normalized:
            # Очистим изображения у всех похожих товаров
            for product in similar_products:
                await session.execute(delete(ProductImage).where(ProductImage.good_id == product.good_id))
            await session.commit()
            await session.refresh(db_product)
            return db_product

        # Отсортируем по order и выставим главный для первого
        normalized.sort(key=lambda i: i["order"]) 
        normalized[0]["is_main"] = True

        # Для каждого товара с таким же артикулом пересоздаем изображения
        for product in similar_products:
            # Удаляем старые
            await session.execute(delete(ProductImage).where(ProductImage.good_id == product.good_id))

            # Добавляем новые по заданному порядку
            for item in normalized:
                session.add(ProductImage(
                    good_id=product.good_id,
                    image_url=item["image_url"],
                    is_main=item["is_main"],
                    order=item["order"],
                ))

        await session.commit()
        await session.refresh(db_product)
        return db_product