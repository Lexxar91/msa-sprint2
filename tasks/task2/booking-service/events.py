import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

import aio_pika
from aio_pika.abc import AbstractExchange

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
EXCHANGE_NAME = "bookings"
ROUTING_KEY_CREATED = "booking.created"


class EventPublisher:
    """Публикация доменных событий в RabbitMQ (topic exchange, durable, persistent)."""

    def __init__(self, url: str = RABBITMQ_URL) -> None:
        self.url = url
        self._connection: Optional[aio_pika.Connection] = None
        self._exchange: Optional[AbstractExchange] = None

    async def connect(self, url: str = RABBITMQ_URL):
        connection = await aio_pika.connect_robust(self.url)
        channel = await connection.channel()
        self._exchange = await channel.declare_exchange(
            EXCHANGE_NAME,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        logging.info("RabbitMQ connected, exchange '%s' ready", EXCHANGE_NAME)


    async def publish_booking_created(self, booking: dict) -> None:
        payload = {
            "event_type": "BookingCreated",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "booking": booking,  # id, user_id, hotel_id, promo_code, discount_percent, price, created_at
        }
        message = aio_pika.Message(
            body=json.dumps(payload).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  # на диск брокера
        )
        await self._exchange.publish(message, routing_key=ROUTING_KEY_CREATED)
        logging.info("Published BookingCreated id=%s", booking.get("id"))

    async def close(self) -> None:
        if self._connection:
            await self._connection.close()