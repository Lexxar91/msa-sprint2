import asyncio
import json
import logging
import os

import aio_pika

from history_db import HistoryDB

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
EXCHANGE_NAME = "bookings"
QUEUE_NAME = "booking.history"
ROUTING_KEY = "booking.created"
RETRY_ATTEMPTS = int(os.getenv("RABBITMQ_RETRY_ATTEMPTS", "12"))
RETRY_DELAY = int(os.getenv("RABBITMQ_RETRY_DELAY", "5"))


async def connect_with_retry(url: str, attempts: int, delay: int):
    """Подключаемся к RabbitMQ с ретраями: брокер мог ещё не поднять AMQP-слушатель."""
    for attempt in range(1, attempts + 1):
        try:
            return await aio_pika.connect_robust(url)
        except Exception as exc:  # noqa: BLE001
            if attempt == attempts:
                raise
            logging.warning(
                "RabbitMQ недоступен (%s), попытка %d/%d — повтор через %dс",
                exc, attempt, attempts, delay,
            )
            await asyncio.sleep(delay)


async def main() -> None:
    db = HistoryDB()
    await db.init_schema()

    connection = await connect_with_retry(RABBITMQ_URL, RETRY_ATTEMPTS, RETRY_DELAY)
    channel = await connection.channel()
    # prefetch=1: не давать consumer'у больше одного сообщения, пока не ACKнет текущее.
    # Защита от того, чтобы один упавший consumer «набрал» кучу сообщений и все их потерял.
    await channel.set_qos(prefetch_count=1)

    exchange = await channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True)
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key=ROUTING_KEY)

    logging.info("history-service listening on queue '%s'", QUEUE_NAME)
    async with queue.iterator() as it:
        async for message in it:
            async with message.process():           # ACK при успехе / NACK+requeue при падении
                event = json.loads(message.body)
                if event.get("event_type") == "BookingCreated":
                    await db.save_booking_created(event["booking"])
                    logging.info("Saved history for booking id=%s", event["booking"].get("id"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())