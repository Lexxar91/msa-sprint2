"""Временный скрипт прослушивания событий из RabbitMQ.

В дальнейшем будет перенесён в booking-history-service.
"""

import asyncio
import json
import os

import aio_pika

RABBITMQ_URL: str = os.getenv(
    "RABBITMQ_URL", "amqp://guest:guest@localhost:5672/"
)
EXCHANGE_NAME: str = "bookings"
QUEUE_NAME: str = "booking.history"
ROUTING_KEY: str = "booking.created"


async def main() -> None:
    """Подключается к RabbitMQ и выводит события бронирования в консоль."""
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        aio_pika.ExchangeType.TOPIC,
        durable=True,
    )
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key=ROUTING_KEY)

    print(f"Listening on queue '{QUEUE_NAME}'...")
    async with queue.iterator() as it:
        async for message in it:
            async with message.process():
                event = json.loads(message.body)
                print(
                    "EVENT:", json.dumps(event, ensure_ascii=False, indent=2)
                )


if __name__ == "__main__":
    asyncio.run(main())
