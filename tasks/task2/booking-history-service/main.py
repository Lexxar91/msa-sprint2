"""Модуль запуска сервиса истории бронирований, потребляющего события из RabbitMQ."""

import asyncio
import json
import logging
import os

import aio_pika

from history_db import HistoryDB

RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
EXCHANGE_NAME: str = "bookings"
QUEUE_NAME: str = "booking.history"
ROUTING_KEY: str = "booking.created"
RETRY_ATTEMPTS: int = int(os.getenv("RABBITMQ_RETRY_ATTEMPTS", "12"))
RETRY_DELAY: int = int(os.getenv("RABBITMQ_RETRY_DELAY", "5"))


async def connect_with_retry(url: str, attempts: int, delay: int):
    """Подключается к RabbitMQ с повторными попытками.

    Брокер может быть ещё не готов принимать AMQP-соединения,
    поэтому выполняем несколько попыток с задержкой.

    Args:
        url: URL для подключения к RabbitMQ.
        attempts: Максимальное количество попыток.
        delay: Задержка между попытками в секундах.

    Returns:
        aio_pika.Connection: Установленное соединение.

    Raises:
        Exception: Если все попытки исчерпаны.
    """
    for attempt in range(1, attempts + 1):
        try:
            return await aio_pika.connect_robust(url)
        except Exception as exc:  # noqa: BLE001
            if attempt == attempts:
                raise
            logging.warning(
                "RabbitMQ unavailable (%s), attempt %d/%d — retry in %ds",
                exc, attempt, attempts, delay,
            )
            await asyncio.sleep(delay)


async def main() -> None:
    """Запускает consumer событий бронирования и сохраняет их в историю."""
    db = HistoryDB()
    await db.open()
    await db.init_schema()

    try:
        connection = await connect_with_retry(
            RABBITMQ_URL,
            RETRY_ATTEMPTS,
            RETRY_DELAY,
        )
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            EXCHANGE_NAME,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        await queue.bind(exchange, routing_key=ROUTING_KEY)

        logging.info("history-service listening on queue '%s'", QUEUE_NAME)

        async with queue.iterator() as it:
            async for message in it:
                async with message.process():
                    event = json.loads(message.body)

                    if event.get("event_type") == "BookingCreated":
                        await db.save_booking_created(event["booking"])
                        logging.info(
                            "Saved history for booking id=%s",
                            event["booking"].get("id"),
                        )
    finally:
        await db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())