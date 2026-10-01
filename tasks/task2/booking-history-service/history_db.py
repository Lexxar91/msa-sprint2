"""Модуль доступа к БД истории бронирований."""

import os
from datetime import datetime

import psycopg
from psycopg_pool import AsyncConnectionPool

HISTORY_DB_URL: str = os.getenv(
    "HISTORY_DB_URL",
    "postgresql://history:history@history-db:5432/history",
)

SCHEMA_SQL: str = """
CREATE TABLE IF NOT EXISTS booking_history (
    booking_id       TEXT PRIMARY KEY,
    user_id          TEXT NOT NULL,
    hotel_id         TEXT NOT NULL,
    promo_code       TEXT,
    discount_percent NUMERIC(10,2),
    price            NUMERIC(10,2) NOT NULL,
    booked_at        TIMESTAMPTZ NOT NULL,
    processed_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE OR REPLACE VIEW stats_by_user AS
SELECT user_id, count(*) AS bookings_count, sum(price) AS total_revenue,
       sum(discount_percent) AS total_discount
FROM booking_history GROUP BY user_id;

CREATE OR REPLACE VIEW stats_by_hotel AS
SELECT hotel_id, count(*) AS bookings_count, sum(price) AS total_revenue
FROM booking_history GROUP BY hotel_id;

CREATE OR REPLACE VIEW stats_by_day AS
SELECT booked_at::date AS day, count(*) AS bookings_count, sum(price) AS total_revenue
FROM booking_history GROUP BY booked_at::date;
"""


class HistoryDB:
    """Асинхронный слой доступа к базе данных истории бронирований."""

    def __init__(self, dsn: str = HISTORY_DB_URL) -> None:
        """Инициализирует подключение к БД истории.

        Args:
            dsn: Строка подключения к БД.
        """
        self.dsn = dsn
        self.pool = AsyncConnectionPool(
            conninfo=dsn, min_size=1, max_size=10, open=False
        )

    async def open(self) -> None:
        """Открывает пул соединений."""
        await self.pool.open()

    async def close(self) -> None:
        """Закрывает пул соединений."""
        await self.pool.close()

    async def init_schema(self) -> None:
        """Создаёт таблицу booking_history и представления статистики."""
        async with self.pool.connection() as conn:
            await conn.execute(SCHEMA_SQL)

    async def save_booking_created(self, booking: dict) -> None:
        """Сохраняет событие о создании бронирования в историю.

        Использует ON CONFLICT DO NOTHING для идемпотентности —
        дубль события не создаст вторую строку.

        Args:
            booking: Словарь с данными бронирования.
        """
        async with self.pool.connection() as conn:
            await conn.execute(
                """
                INSERT INTO booking_history
                    (booking_id, user_id, hotel_id, promo_code,
                     discount_percent, price, booked_at)
                VALUES
                    (%(booking_id)s, %(user_id)s, %(hotel_id)s, %(promo_code)s,
                     %(discount_percent)s, %(price)s, %(booked_at)s)
                ON CONFLICT (booking_id) DO NOTHING
                """,
                {
                    "booking_id": str(booking["id"]),
                    "user_id": booking["user_id"],
                    "hotel_id": booking["hotel_id"],
                    "promo_code": booking.get("promo_code") or None,
                    "discount_percent": booking["discount_percent"],
                    "price": booking["price"],
                    "booked_at": datetime.fromisoformat(booking["created_at"]),
                },
            )
