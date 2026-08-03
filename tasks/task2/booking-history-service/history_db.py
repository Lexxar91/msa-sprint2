import os
from datetime import datetime

import psycopg

# Локально: postgresql://history:history@localhost:5434/history
HISTORY_DB_URL = os.getenv("HISTORY_DB_URL", "postgresql://history:history@history-db:5432/history")

SCHEMA_SQL = """
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
    def __init__(self, dsn: str = HISTORY_DB_URL) -> None:
        self.dsn = dsn

    async def init_schema(self) -> None:
        async with await psycopg.AsyncConnection.connect(self.dsn) as conn:
            await conn.execute(SCHEMA_SQL)

    async def save_booking_created(self, booking: dict) -> None:
        # ON CONFLICT DO NOTHING = идемпотентность: дубль события не создаст вторую строку.
        async with await psycopg.AsyncConnection.connect(self.dsn) as conn:
            await conn.execute(
                """
                INSERT INTO booking_history
                    (booking_id, user_id, hotel_id, promo_code, discount_percent, price, booked_at)
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