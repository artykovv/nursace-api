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

    # Объявляем очередь, если не существует
    channel.queue_declare(queue=RABBITMQ_VHOST, durable=True)

    # Публикуем сообщение
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_VHOST,
        body=message_body.encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=2  # Сделать сообщение устойчивым
        )
    )

    print(f"[DEBUG] Заказ #{order.id} отправлен в очередь send_order_check")
    connection.close()