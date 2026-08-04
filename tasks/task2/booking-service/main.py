"""Модуль запуска асинхронного gRPC-сервера BookingService."""

import asyncio
import logging
import os
import sys

import grpc

sys.path.append(os.path.join(os.path.dirname(__file__), "proto"))
import booking_pb2_grpc  # noqa: E402

from server import BookingServiceServicer  # noqa: E402
from repository import BookingRepository
from service import BookingService
from monolith_client import MonolithClient
from events import EventPublisher

GRPC_PORT: int = int(os.getenv("GRPC_PORT", "9090"))


async def serve() -> None:
    """Запускает асинхронный gRPC-сервер BookingService и блокирует до остановки.

    Создаёт сервер на базе ``grpc.aio`` (совместим с asyncio, что нужно для
    последующих async-вызовов httpx и aio-pika), регистрирует servicer,
    открывает незашифрованный порт на всех сетевых интерфейсах и работает до
    получения сигнала завершения (SIGTERM/SIGINT).

    Порт прослушивания задаётся переменной окружения ``GRPC_PORT``
    (по умолчанию 9090).

    Raises:
        RuntimeError: если не удалось привязаться к указанному порту.
    """
    repository = BookingRepository()
    await repository.init_schema()

    publisher = EventPublisher()
    await publisher.connect()

    service = BookingService(MonolithClient(), repository, publisher)
    server = grpc.aio.server()  # type: ignore[attr-defined]
    booking_pb2_grpc.add_BookingServiceServicer_to_server(
        BookingServiceServicer(service), server,
    )
    listen_addr = f"[::]:{GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    logging.info("gRPC server listening on %s", listen_addr)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())