import os
from typing import Optional

import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://booking:booking@booking-db:5432/booking")


CREATE_TABLE_SQL = """
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


COLUMNS = ("id", "user_id", "hotel_id", "promo_code", "discount_percent", "price", "created_at")


class BookingRepository:
    """Доступ к booking-db через psycopg (async). Один коннект на операцию — просто;
    в продакшене держат пул (psycopg_pool.AsyncConnectionPool)."""

    def __init__(self, dsn: str = DATABASE_URL) -> None:
        self.dsn = dsn

    async def init_schema(self) -> None:
        async with await psycopg.AsyncConnection.connect(self.dsn) as conn:
            await conn.execute(CREATE_TABLE_SQL)

    async def save(self, booking: dict) -> dict:
        async with await psycopg.AsyncConnection.connect(self.dsn) as conn:
            async with conn.cursor() as cur:
                # RETURNING вернёт то, что сгенерировала БД: id и created_at (DEFAULT now()).
                await cur.execute(
                    """
                    INSERT INTO booking (user_id, hotel_id, promo_code, discount_percent, price)
                    VALUES (%(user_id)s, %(hotel_id)s, %(promo_code)s, %(discount_percent)s, %(price)s)
                    RETURNING id, created_at
                    """,
                    booking,
                )
                row = await cur.fetchone()
        # async with conn сделал commit при успешном выходе.
        return {
            **booking,
            "id": str(row[0]),
            "created_at": row[1].isoformat(),
        }

    async def find_by_user(self, user_id: str) -> list[dict]:
        async with await psycopg.AsyncConnection.connect(self.dsn) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    f"SELECT {', '.join(COLUMNS)} FROM booking WHERE user_id = %s ORDER BY id",
                    (user_id,),
                )
                rows = await cur.fetchall()
        return [self._to_dict(r) for r in rows]

    @staticmethod
    def _to_dict(row: tuple) -> dict:
        d = dict(zip(COLUMNS, row))
        d["id"] = str(d["id"])
        d["discount_percent"] = float(d["discount_percent"])  # Decimal -> float для proto double
        d["price"] = float(d["price"])
        d["created_at"] = d["created_at"].isoformat()
        return d