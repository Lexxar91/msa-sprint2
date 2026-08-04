"""Модуль бизнес-логики бронирования."""

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
        publisher: EventPublisher,
    ) -> None:
        """Инициализирует сервис бронирования.

        Args:
            client: Клиент для взаимодействия с монолитным приложением.
            repository: Репозиторий для доступа к БД бронирований.
            publisher: Публикатор событий в RabbitMQ.
        """
        self.client = client
        self.repository = repository
        self.publisher = publisher

    async def create_booking(
        self, user_id: str, hotel_id: str, promo_code: str,
    ) -> dict:
        """Создаёт новое бронирование.

        Выполняет валидацию пользователя и отеля, рассчитывает цену со скидкой,
        сохраняет бронирование в БД и публикует событие BookingCreated.

        Args:
            user_id: Идентификатор пользователя.
            hotel_id: Идентификатор отеля.
            promo_code: Промокод (может быть пустым).

        Returns:
            dict: Данные сохранённого бронирования с полями id, user_id, hotel_id,
                  promo_code, discount_percent, price, created_at.
        """
        await self._validate_user(user_id)
        await self._validate_hotel(hotel_id)
        base_price = await self._resolve_base_price(user_id)
        discount = await self._resolve_promo_discount(promo_code, user_id)
        final_price = base_price - discount

        saved = await self.repository.save({
            "user_id": user_id,
            "hotel_id": hotel_id,
            "promo_code": promo_code or "",
            "discount_percent": discount,
            "price": final_price,
        })
        await self.publisher.publish_booking_created(saved)
        return saved

    async def list_bookings(self, user_id: str) -> list[dict]:
        """Возвращает список бронирований пользователя.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            list[dict]: Список бронирований пользователя.
        """
        return await self.repository.find_by_user(user_id)

    async def _validate_user(self, user_id: str) -> None:
        """Проверяет, что пользователь активен и не в чёрном списке."""
        if not await self.client.is_user_active(user_id):
            raise ValueError("User is inactive")
        if await self.client.is_user_blacklisted(user_id):
            raise ValueError("User is blacklisted")

    async def _validate_hotel(self, hotel_id: str) -> None:
        """Проверяет, что отель работает, является доверенным и не забронирован полностью."""
        if not await self.client.is_hotel_operational(hotel_id):
            raise ValueError("Hotel is not operational")
        if not await self.client.is_hotel_trusted(hotel_id):
            raise ValueError("Hotel is not trusted based on reviews")
        if await self.client.is_hotel_fully_booked(hotel_id):
            raise ValueError("Hotel is fully booked")

    async def _resolve_base_price(self, user_id: str) -> float:
        """Определяет базовую цену в зависимости от статуса пользователя.

        VIP-пользователи получают скидку к базовой цене (80.0 вместо 100.0).
        """
        status = await self.client.get_user_status(user_id)
        return 80.0 if status and status.upper() == "VIP" else 100.0

    async def _resolve_promo_discount(self, promo_code: str, user_id: str) -> float:
        """Рассчитывает скидку по промокоду.

        Если промокод не указан или невалиден, возвращает 0.0.
        """
        if not promo_code:
            return 0.0
        promo = await self.client.validate_promo(promo_code, user_id)
        if promo is None:
            return 0.0
        return float(promo.get("discount", 0.0))
