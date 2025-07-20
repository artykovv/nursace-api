from decimal import Decimal
import json
import pika
from config.config import RABBITMQ_HOST, RABBITMQ_PASSWORD, RABBITMQ_PORT, RABBITMQ_USERNAME, RABBITMQ_VHOST


def send_lead_to_rabbitmq(lead):
    info = {
        "lead_id": lead.id,
        "full_name": lead.full_name,
        "phone": lead.phone_number,
        "comment": lead.comment,
        "status": lead.status.name if lead.status else None,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "products": [
            {
                "product_name": item.product.good_name if item.product else "Неизвестный товар",
                "quantity": item.quantity,
                "product_id": item.product_id
            }
            for item in lead.products
        ]
    }

    # Сериализация
    message_body = json.dumps(info, ensure_ascii=False)

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

    # Объявление exchange и очереди
    channel.exchange_declare(
        exchange='nursace_leads_exchange',
        exchange_type='direct',
        durable=True
    )

    channel.queue_declare(queue="lead_notifications", durable=True)

    channel.queue_bind(
        exchange='nursace_leads_exchange',
        queue='lead_notifications',
        routing_key='nursace.lead.created'
    )

    # Отправка сообщения
    channel.basic_publish(
        exchange='nursace_leads_exchange',
        routing_key="nursace.lead.created",
        body=message_body.encode("utf-8"),
        properties=pika.BasicProperties(
            delivery_mode=2  # Устойчивое сообщение
        )
    )

    print(f"[DEBUG] Лид #{lead.id} отправлен в очередь lead_notifications")
    connection.close()