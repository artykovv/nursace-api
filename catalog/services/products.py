from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from catalog.models import Product
from catalog.models.product_images import ProductImage
from catalog.schemas.product import ProductImageSchema, UpdateProductSchema

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
        for key, value in update_data.items():
            setattr(db_product, key, value)

        try:
            await session.commit()
            await session.refresh(db_product)
            return db_product
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=f"Error updating product: {str(e)}")
    
    async def update_product_images(session: AsyncSession, product_id: int, images: List[ProductImageSchema]):
        result = await session.execute(
            select(Product).options(selectinload(Product.images)).where(Product.good_id == product_id)
        )
        db_product = result.scalar_one_or_none()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Получаем артикул текущего товара
        current_articul = db_product.articul
        
        # Находим все товары с тем же артикулом
        similar_products_result = await session.execute(
            select(Product).options(selectinload(Product.images)).where(Product.articul == current_articul)
        )
        similar_products = similar_products_result.scalars().all()
        
        # Получаем уже существующие URL для текущего товара
        existing_urls = {img.image_url for img in db_product.images}

        # Добавляем изображения к текущему товару
        for image in images:
            if image.image_url not in existing_urls:
                db_image = ProductImage(
                    good_id=product_id,
                    image_url=image.image_url,
                    is_main=image.is_main,
                    order=image.order
                )
                session.add(db_image)
                existing_urls.add(image.image_url)  # Чтобы при нескольких одинаковых URL в запросе не дублировало

        # Добавляем изображения ко всем похожим товарам с тем же артикулом
        for similar_product in similar_products:
            if similar_product.good_id != product_id:  # Пропускаем текущий товар
                # Получаем существующие URL для похожего товара
                similar_existing_urls = {img.image_url for img in similar_product.images}
                
                for image in images:
                    if image.image_url not in similar_existing_urls:
                        similar_image = ProductImage(
                            good_id=similar_product.good_id,
                            image_url=image.image_url,
                            is_main=image.is_main,
                            order=image.order
                        )
                        session.add(similar_image)

        await session.commit()
        await session.refresh(db_product)
        return db_product