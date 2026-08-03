import os
from typing import Any, Optional

import httpx

MONOLITH_BASE_URL = os.getenv("MONOLITH_BASE_URL", "http://monolith:8080")
TIMEOUT = 5.0


class MonolithError(RuntimeError):
    """Исключение, возникающее при ошибках взаимодействия с монолитом.

    Используется для обработки сетевых ошибок, таймаутов, а также ошибок
    на стороне сервера (5xx) или неожиданных ошибок клиента (4xx, кроме 400/404).
    """
    pass


class MonolithClient:
    """Клиент для взаимодействия с монолитным приложением Hotelio.

    Этот клиент отвечает исключительно за транспортный уровень: выполнение HTTP-запросов
    к API монолита и возврат полученных данных. Бизнес-логика обработки этих
    данных должна быть реализована на уровне сервисов.

    Attributes:
        base_url (str): Базовый URL адрес монолита.
    """

    def __init__(self, base_url: str = MONOLITH_BASE_URL) -> None:
        self.base_url = base_url

    async def _request(
            self, method: str, 
            path: str, 
            params: Optional[dict] = None,
            as_text: bool = False
    ) -> Any:
        """Выполняет HTTP-запрос к монолиту.

        Args:
            method (str): HTTP метод (GET, POST и т.д.).
            path (str): Путь к эндпоинту.
            params (Optional[dict]): Параметры запроса.

        Returns:
            Any: JSON-ответ в случае успеха (200 OK), None в случае 400 или 404,
                 или вызывает MonolithError при других статус-кодах или сетевых ошибках.

        Raises:
            MonolithError: Если произошла сетевая ошибка или сервер вернул ошибку (не 400/404).
        """
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=TIMEOUT) as client:
                r = await client.request(method, path, params=params)
        except httpx.HTTPError as exc:
            raise MonolithError(f"network error {method} {path}: {exc}") from exc

        if r.status_code in (400, 404):
            return None
        if r.status_code >= 400:
            raise MonolithError(f"monolith {r.status_code} on {method} {path}")
        return r.text if as_text else r.json()      # <-- единственная новая строка

    async def _get_bool(self, path: str) -> bool:
        """Вспомогательный метод для получения булевого значения из ответа."""
        return bool(await self._request("GET", path))

    async def is_user_active(self, user_id: str) -> bool:
        """Проверяет, является ли пользователь активным."""
        return await self._get_bool(f"/api/users/{user_id}/active")

    async def is_user_blacklisted(self, user_id: str) -> bool:
        """Проверяет, находится ли пользователь в черном списке."""
        return await self._get_bool(f"/api/users/{user_id}/blacklisted")

    async def is_user_authorized(self, user_id: str) -> bool:
        """Проверяет, авторизован ли пользователь."""
        return await self._get_bool(f"/api/users/{user_id}/authorized")

    async def get_hotel(self, hotel_id: str) -> Optional[dict]:
        """Получает информацию о отеле."""
        return await self._request("GET", f"/api/hotels/{hotel_id}")

    async def is_hotel_operational(self, hotel_id: str) -> bool:
        """Проверяет, работает ли отель."""
        return await self._get_bool(f"/api/hotels/{hotel_id}/operational")

    async def is_hotel_fully_booked(self, hotel_id: str) -> bool:
        """Проверяет, полностью ли забронирован отель."""
        return await self._get_bool(f"/api/hotels/{hotel_id}/fully-booked")

    async def validate_promo(self, code: str, user_id: str) -> Optional[dict]:
        """Проверяет применимость промокода для пользователя."""
        return await self._request(
            "POST", "/api/promos/validate", params={"code": code, "userId": user_id}
        )

    async def is_hotel_trusted(self, hotel_id: str) -> bool:
        """Проверяет, является ли отель доверенным."""
        return await self._get_bool(f"/api/reviews/hotel/{hotel_id}/trusted")


    async def get_user_status(self, user_id: str) -> Optional[str]:
        raw = await self._request("GET", f"/api/users/{user_id}/status", as_text=True)
        if raw is None:
            return None
        return raw.strip().strip('"')   