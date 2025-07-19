from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from order.models import Order, OrderItem, OrderInfo
from catalog.models import Product
from decimal import Decimal
import aiosmtplib
from email.message import EmailMessage
from config.config import SMTP_USER, SMTP_PASS, SMTP_HOST, SMTP_PORT
from config.database import async_session_maker
from rabbitmq.send import send_order_to_rabbitmq

async def send_check_email(order_id: int):
    print(f"[DEBUG] Запуск отправки чека по заказу ID = {order_id}")

    async with async_session_maker() as db:
        # Получаем заказ
        result = await db.execute(
            select(Order).where(Order.id == order_id).options(
                selectinload(Order.items).selectinload(OrderItem.product),
                selectinload(Order.info)
            )
        )
        order = result.scalar_one_or_none()
        print(f"[DEBUG] Найден заказ: {order is not None}")
        if not order:
            raise ValueError(f"Заказ с ID {order_id} не найден")
        # отправляем в rabbitMQ
        send_order_to_rabbitmq(order)

        info = order.info
        print(f"[DEBUG] Информация о заказе: email={info.email}, name={info.first_name} {info.last_name}")

        items = order.items
        print(f"[DEBUG] Найдено товаров в заказе: {len(items)}")

        to_email = info.email
        full_name = f"{info.first_name} {info.last_name}"
        address = f"{info.region}, г. {info.city}, {info.address_line1}, {info.postal_code}"
        total = order.total_price or Decimal("0.00")

        rows = ""
        for item in items:
            product = item.product
            product_name = product.good_name if product else "Неизвестный товар"
            print(f"[DEBUG] Товар: {product_name}, Кол-во: {item.quantity}, Цена: {item.price}")
            rows += f"""
                <tr>
                    <td>{product_name}</td>
                    <td align="center">{item.quantity}</td>
                    <td align="right">{item.price:.2f} сом</td>
                </tr>
            """

        html_body = f"""
        <html>
        <body>
            <h2>Чек за заказ №{order_id}</h2>
            <p><strong>ФИО:</strong> {full_name}</p>
            <p><strong>Адрес доставки:</strong> {address}</p>
            <p><strong>Телефон:</strong> {info.phone}</p>

            <h3>Состав заказа:</h3>
            <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
                <thead>
                    <tr>
                        <th>Товар</th>
                        <th>Кол-во</th>
                        <th>Цена</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                    <tr>
                        <td colspan="2" align="right"><strong>Итого:</strong></td>
                        <td align="right"><strong>{total:.2f} сом</strong></td>
                    </tr>
                </tbody>
            </table>

            <p>Спасибо за покупку!</p>
            <p>С уважением,<br>команда <strong>Style Shoes</strong></p>
        </body>
        </html>
        """

        # Создаем email
        msg = EmailMessage()
        msg["From"] = f"Style Shoes <{SMTP_USER}>"
        msg["To"] = to_email
        msg["Subject"] = f"Чек за заказ №{order_id}"

        msg.set_content("Ваш заказ был успешно оплачен. Смотрите HTML-версию письма.")
        msg.add_alternative(html_body, subtype="html")

        print(f"[DEBUG] Письмо подготовлено. Отправка на: {to_email}")

        try:
            smtp = aiosmtplib.SMTP(hostname=SMTP_HOST, port=SMTP_PORT, start_tls=True)
            await smtp.connect()
            await smtp.login(SMTP_USER, SMTP_PASS)
            await smtp.send_message(msg)
            await smtp.quit()
            print(f"[DEBUG] Письмо успешно отправлено на {to_email}")
        except Exception as e:
            print(f"[ERROR] Ошибка при отправке письма: {e}")