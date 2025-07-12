from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from lxml import etree  # pip install lxml
from sqlalchemy.orm import selectinload

from config.database import get_async_session
from catalog.models import Product

router = APIRouter(prefix="/facebook", tags=["facebook"])

@router.get("/facebook-feed.xml", response_class=Response)
async def facebook_feed(session: AsyncSession = Depends(get_async_session)):
    # Получаем товары, которые нужно отображать
    result = await session.execute(
        select(Product)
        .where(Product.display == 1)
        .options(
            selectinload(Product.manufacturer),
            selectinload(Product.images),
            selectinload(Product.color),
            selectinload(Product.season),
            selectinload(Product.sex),
            selectinload(Product.collection),
            selectinload(Product.material),
            selectinload(Product.measure_unit),
            selectinload(Product.guarantee_mes_unit),
        )
    )
    products = result.scalars().all()

    # Создаем XML-элемент
    rss = etree.Element("rss", version="2.0")
    channel = etree.SubElement(rss, "channel")
    etree.SubElement(channel, "title").text = "Product Feed"
    etree.SubElement(channel, "link").text = "https://yourdomain.com/facebook/facebook-feed.xml"
    etree.SubElement(channel, "description").text = "Product feed for Facebook catalog"

    for product in products:
        item = etree.SubElement(channel, "item")
        etree.SubElement(item, "id").text = str(product.good_id)
        etree.SubElement(item, "title").text = product.good_name or ""
        etree.SubElement(item, "description").text = product.description or ""
        etree.SubElement(item, "availability").text = "in stock"
        etree.SubElement(item, "condition").text = "new"
        etree.SubElement(item, "price").text = f"{product.retail_price:.2f} KGS"
        etree.SubElement(item, "link").text = f"https://yourdomain.com/product/{product.good_id}"

        # Первое изображение
        if product.images:
            etree.SubElement(item, "image_link").text = product.images[0].image_url

        # Доп. изображения
        for img in product.images[1:5]:  # до 5 изображений
            etree.SubElement(item, "additional_image_link").text = img.image_url

        # Бренд, категория и т.п.
        if product.manufacturer:
            etree.SubElement(item, "brand").text = product.manufacturer.manufacturer_name

        if product.color:
            etree.SubElement(item, "color").text = product.color.color_name

        if product.product_size:
            etree.SubElement(item, "size").text = str(product.product_size)

    # Преобразуем в XML-строку
    xml_string = etree.tostring(rss, xml_declaration=True, encoding='UTF-8', pretty_print=True)

    return Response(content=xml_string, media_type="application/xml")