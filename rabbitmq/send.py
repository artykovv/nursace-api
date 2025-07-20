from decimal import Decimal
import json
import pika
from config.config import RABBITMQ_HOST, RABBITMQ_PASSWORD, RABBITMQ_PORT, RABBITMQ_USERNAME, RABBITMQ_VHOST

def send_order_to_rabbitmq(order):
    # Извлечение информации из заказа
    info = order.info
    items = order.items
    total = str(order.total_price or Decimal("0.00"))

    order_data = {
        "order_id": order.id,
        "full_name": f"{info.first_name} {info.last_name}",
        "email": info.email,
        "phone": info.phone,
        "address": {
            "region": info.region,
            "city": info.city,
            "line1": info.address_line1,
            "postal_code": info.postal_code,
        },
        "items": [
            {
                "product_name": item.product.good_name if item.product else "Неизвестный товар",
                "quantity": item.quantity,
                "price": str(item.price)
            }
            for item in items
        ],
        "total": total
    }

    # Сериализация в JSON
    message_body = json.dumps(order_data, ensure_ascii=False)

    # Подключение к RabbitMQ
    credentials = pika.PlainCredentials(RABBITMQ_USERNAME, RABBITMQ_PASSWORD)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
    )

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # Объявляем exchange
    channel.exchange_declare(
        exchange='nursace_orders_exchange',
        exchange_type='direct',
        durable=True
    )

    # Объявляем очередь
    channel.queue_declare(queue="order_notifications", durable=True)

    # Связываем exchange и очередь через routing_key
    channel.queue_bind(
        exchange='nursace_orders_exchange',
        queue='order_notifications',
        routing_key='nursace.order.success'
    )

    # Публикуем сообщение
    channel.basic_publish(
        exchange='nursace_orders_exchange',
        routing_key="nursace.order.success",
        body=message_body.encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=2  # Сделать сообщение устойчивым
        )
    )

    print(f"[DEBUG] Заказ #{order.id} отправлен в очередь send_order_check")
    connection.close()