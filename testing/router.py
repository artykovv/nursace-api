from fastapi import APIRouter, Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session

from catalog.models import Product, Category, Manufacturer, Collection, Season, Sex, Color, Material, MeasureUnit, Currency, ProductAttribute, ProductCurrencyPrice, Analog, ProductImage
from order.models import OrderItem
from cart.models import CartItem

router = APIRouter(prefix="/test")

@router.delete("/delete/catalog")
async def delete_catalog(session: AsyncSession = Depends(get_async_session)):
    models = [
        OrderItem,
        CartItem,
        ProductImage,
        Analog,
        ProductCurrencyPrice,
        ProductAttribute,
        Product,
        Category,
        Collection,
        Manufacturer,
        Season,
        Sex,
        Color,
        Material,
        MeasureUnit,
        Currency,
    ]

    for model in models:
        await session.execute(delete(model))

    await session.commit()
    return {"detail": "Catalog deleted successfully"}