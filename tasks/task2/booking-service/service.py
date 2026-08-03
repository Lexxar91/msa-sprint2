import uuid
from datetime import datetime, timezone

from monolith_client import MonolithClient
from repository import BookingRepository
from events import EventPublisher

class BookingService:
    """Бизнес-логика бронирования. Зеркалит BookingService.java из монолита.

    Порядок: validateUser -> validateHotel -> resolveBasePrice -> resolvePromoDiscount.
    Данные берём через REST (monolith_client), логику не переносим.
    """

    def __init__(
        self, 
        client: MonolithClient,
        repository: BookingRepository,
        publisher: EventPublisher
    ) -> None:
        self.client = client
        self.repository = repository
        self.publisher = publisher

    async def create_booking(self, user_id, hotel_id, promo_code) -> dict:
        await self._validate_user(user_id)
        await self._validate_hotel(hotel_id)
        base_price = await self._resolve_base_price(user_id)
        discount = await self._resolve_promo_discount(promo_code, user_id)
        final_price = base_price - discount

        saved = await self.repository.save({          # <-- реальное сохранение
            "user_id": user_id,
            "hotel_id": hotel_id,
            "promo_code": promo_code or "",
            "discount_percent": discount,
            "price": final_price,
        })
        # TODO(events): опубликовать BookingCreated в RabbitMQ (следующий шаг).
        await self.publisher.publish_booking_created(saved)
        return saved

    async def list_bookings(self, user_id: str) -> list[dict]:
        return await self.repository.find_by_user(user_id) 

    # ---- Валидации: тексты ошибок ТОЧНО как в Java ----
    async def _validate_user(self, user_id: str) -> None:
        if not await self.client.is_user_active(user_id):
            raise ValueError("User is inactive")
        if await self.client.is_user_blacklisted(user_id):
            raise ValueError("User is blacklisted")

    async def _validate_hotel(self, hotel_id: str) -> None:
        if not await self.client.is_hotel_operational(hotel_id):
            raise ValueError("Hotel is not operational")
        if not await self.client.is_hotel_trusted(hotel_id):
            raise ValueError("Hotel is not trusted based on reviews")
        if await self.client.is_hotel_fully_booked(hotel_id):
            raise ValueError("Hotel is fully booked")

    # ---- Расчёт цены ----
    async def _resolve_base_price(self, user_id: str) -> float:
        status = await self.client.get_user_status(user_id)  # "ACTIVE" / "VIP" / None
        return 80.0 if status and status.upper() == "VIP" else 100.0

    async def _resolve_promo_discount(self, promo_code: str, user_id: str) -> float:
        if not promo_code:
            return 0.0
        promo = await self.client.validate_promo(promo_code, user_id)  # dict или None
        if promo is None:
            return 0.0  # невалидный промо -> скидка 0, НЕ ошибка
        return float(promo.get("discount", 0.0))
