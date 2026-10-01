"""Модуль доступа к БД бронирований через psycopg."""

import os
from typing import Optional

import psycopg

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://booking:booking@booking-db:5432/booking",
)

CREATE_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS booking (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    hotel_id VARCHAR(255),
    promo_code VARCHAR(255),
    discount_percent NUMERIC(10, 2),
    price            NUMERIC(10, 2) NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""

COLUMNS: tuple[str, ...] = (
    "id",
    "user_id",
    "hotel_id",
    "promo_code",
    "discount_percent",
    "price",
    "created_at",
)


class BookingRepository:
    """Доступ к booking-db через psycopg (async).

    Один коннект на операцию — просто; в продакшене держат пул
    (psycopg_pool.AsyncConnectionPool).
    """

    def __init__(self, dsn: str = DATABASE_URL) -> None:
        """Инициализирует репозиторий.

        Args:
            dsn: Строка подключения к БД.
        """
        self.dsn = dsn

    async def init_schema(self) -> None:
        """Создаёт таблицу booking, если она ещё не существует."""
        async with await psycopg.AsyncConnection.connect(self.dsn) as conn:
            await conn.execute(CREATE_TABLE_SQL)

    async def save(self, booking: dict) -> dict:
        """Сохраняет новое бронирование в БД.

        Args:
            booking: Словарь с данными бронирования.

        Returns:
            dict: Данные бронирования с заполненными id и created_at.
        """
        async with await psycopg.AsyncConnection.connect(self.dsn) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO booking
                        (user_id, hotel_id, promo_code, discount_percent, price)
                    VALUES
                        (%(user_id)s, %(hotel_id)s, %(promo_code)s,
                         %(discount_percent)s, %(price)s)
                    RETURNING id, created_at
                    """,
                    booking,
                )
                row = await cur.fetchone()
        return {
            **booking,
            "id": str(row[0]),
            "created_at": row[1].isoformat(),
        }

    async def find_by_user(self, user_id: str) -> list[dict]:
        """Возвращает список бронирований пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            list[dict]: Список бронирований пользователя.
        """
        async with await psycopg.AsyncConnection.connect(self.dsn) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"SELECT {', '.join(COLUMNS)} FROM booking "
                    "WHERE user_id = %s ORDER BY id",
                    (user_id,),
                )
                rows = await cur.fetchall()
        return [self._to_dict(row) for row in rows]

    @staticmethod
    def _to_dict(row: tuple) -> dict:
        """Преобразует строку из БД в словарь с корректными типами.

        Args:
            row: Строка результата SQL-запроса.

        Returns:
            Результат операции, описанной выше.
        """
        result = dict(zip(COLUMNS, row))
        result["id"] = str(result["id"])
        result["discount_percent"] = float(result["discount_percent"])
        result["price"] = float(result["price"])
        result["created_at"] = result["created_at"].isoformat()
        return result
