# listen_events.py  (временный, для проверки; потом перенесём в booking-history-service)
import asyncio
import json
import os

import aio_pika

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
EXCHANGE_NAME = "bookings"
QUEUE_NAME = "booking.history"
ROUTING_KEY = "booking.created"


async def main() -> None:
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    # Тот же exchange, что и publisher (durable — идемпотентно).
    exchange = await channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True)
    # Очередь потребителя: durable, подписана на booking.created.
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.bind(exchange, routing_key=ROUTING_KEY)

    print(f"Listening on queue '{QUEUE_NAME}'...")
    async with queue.iterator() as it:
        async for message in it:
            # message.process() = ACK при успехе, NACK при исключении.
            async with message.process():
                event = json.loads(message.body)
                print("EVENT:", json.dumps(event, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())