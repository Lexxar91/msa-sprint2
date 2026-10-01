"""Модуль клиента для взаимодействия с монолитным приложением Hotelio."""

import os
from typing import Any, Optional

import httpx

MONOLITH_BASE_URL: str = os.getenv("MONOLITH_BASE_URL", "http://monolith:8080")
TIMEOUT: float = 5.0


class MonolithError(RuntimeError):
    """Исключение при ошибках взаимодействия с монолитом.

    Используется для обработки сетевых ошибок, таймаутов, а также ошибок
    на стороне сервера (5xx) или неожиданных ошибок клиента (4xx, кроме 400/404).
    """


class MonolithClient:
    """Клиент для взаимодействия с монолитным приложением Hotelio.

    Отвечает за транспортный уровень: выполнение HTTP-запросов к API монолита
    и возврат полученных данных. Бизнес-логика обработки этих данных должна
    быть реализована на уровне сервисов.

    Attributes:
        base_url: Базовый URL адрес монолита.
    """

    def __init__(self, base_url: str = MONOLITH_BASE_URL) -> None:
        """Инициализирует клиент.

        Args:
            base_url: Базовый URL адрес монолита.
        """
        self.base_url = base_url

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        as_text: bool = False,
    ) -> Any:
        """Выполняет HTTP-запрос к монолиту.

        Args:
            method: HTTP метод (GET, POST и т.д.).
            path: Путь к эндпоинту.
            params: Параметры запроса.
            as_text: Вернуть ответ как текст (вместо JSON).

        Returns:
            JSON-ответ или текст в случае успеха (200 OK), None в случае 400 или 404.

        Raises:
            MonolithError: При сетевой ошибке или статус-коде >= 400 (кроме 400/404).
        """
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url, timeout=TIMEOUT
            ) as client:
                response = await client.request(method, path, params=params)
        except httpx.HTTPError as exc:
            raise MonolithError(
                f"network error {method} {path}: {exc}"
            ) from exc

        if response.status_code in (400, 404):
            return None
        if response.status_code >= 400:
            raise MonolithError(
                f"monolith {response.status_code} on {method} {path}"
            )
        return response.text if as_text else response.json()

    async def _get_bool(self, path: str) -> bool:
        """Возвращает булево значение из ответа монолита.

        Args:
            path: Путь REST-ресурса.

        Returns:
            Результат операции, описанной выше.
        """
        return bool(await self._request("GET", path))

    async def is_user_active(self, user_id: str) -> bool:
        """Проверяет, активен ли пользователь.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Результат операции, описанной выше.
        """
        return await self._get_bool(f"/api/users/{user_id}/active")

    async def is_user_blacklisted(self, user_id: str) -> bool:
        """Проверяет, находится ли пользователь в чёрном списке.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Результат операции, описанной выше.
        """
        return await self._get_bool(f"/api/users/{user_id}/blacklisted")

    async def is_user_authorized(self, user_id: str) -> bool:
        """Проверяет, авторизован ли пользователь.

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Результат операции, описанной выше.
        """
        return await self._get_bool(f"/api/users/{user_id}/authorized")

    async def get_hotel(self, hotel_id: str) -> Optional[dict]:
        """Возвращает информацию об отеле.

        Args:
            hotel_id: Идентификатор отеля.

        Returns:
            Результат операции, описанной выше.
        """
        return await self._request("GET", f"/api/hotels/{hotel_id}")

    async def is_hotel_operational(self, hotel_id: str) -> bool:
        """Проверяет, работает ли отель.

        Args:
            hotel_id: Идентификатор отеля.

        Returns:
            Результат операции, описанной выше.
        """
        return await self._get_bool(f"/api/hotels/{hotel_id}/operational")

    async def is_hotel_fully_booked(self, hotel_id: str) -> bool:
        """Проверяет, полностью ли забронирован отель.

        Args:
            hotel_id: Идентификатор отеля.

        Returns:
            Результат операции, описанной выше.
        """
        return await self._get_bool(f"/api/hotels/{hotel_id}/fully-booked")

    async def validate_promo(self, code: str, user_id: str) -> Optional[dict]:
        """Проверяет применимость промокода для пользователя.

        Args:
            code: Параметр операции.
            user_id: Идентификатор пользователя.

        Returns:
            Результат операции, описанной выше.
        """
        return await self._request(
            "POST",
            "/api/promos/validate",
            params={"code": code, "userId": user_id},
        )

    async def is_hotel_trusted(self, hotel_id: str) -> bool:
        """Проверяет, является ли отель доверенным.

        Args:
            hotel_id: Идентификатор отеля.

        Returns:
            Результат операции, описанной выше.
        """
        return await self._get_bool(f"/api/reviews/hotel/{hotel_id}/trusted")

    async def get_user_status(self, user_id: str) -> Optional[str]:
        """Возвращает статус пользователя (ACTIVE, VIP или None).

        Args:
            user_id: Идентификатор пользователя.

        Returns:
            Результат операции, описанной выше.
        """
        raw = await self._request(
            "GET", f"/api/users/{user_id}/status", as_text=True
        )
        if raw is None:
            return None
        return raw.strip().strip('"')
