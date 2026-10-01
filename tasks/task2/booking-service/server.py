"""Модуль gRPC-сервера сервиса бронирования."""

import logging

import grpc

import booking_pb2
import booking_pb2_grpc
from service import BookingService


class BookingServiceServicer(booking_pb2_grpc.BookingServiceServicer):
    """Реализация контракта booking.proto на стороне сервера."""

    def __init__(self, service: BookingService) -> None:
        """Инициализирует сервисер.

        Args:
            service: Экземпляр бизнес-логики бронирования.
        """
        self.service = service

    async def CreateBooking(
        self,
        request: booking_pb2.BookingRequest,
        context: grpc.aio.ServicerContext,
    ) -> booking_pb2.BookingResponse:
        """Обрабатывает запрос на создание бронирования.

        Args:
            request: Запрос с данными бронирования.
            context: Контекст gRPC-вызова.

        Returns:
            BookingResponse: Ответ с данными созданного бронирования.
        """
        logging.info(
            "CreateBooking user=%s hotel=%s promo=%r",
            request.user_id,
            request.hotel_id,
            request.promo_code,
        )

        try:
            booking = await self.service.create_booking(
                user_id=request.user_id,
                hotel_id=request.hotel_id,
                promo_code=request.promo_code,
            )
        except ValueError as exc:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(exc))
            return booking_pb2.BookingResponse()
        except Exception as exc:  # noqa: BLE001
            logging.exception("CreateBooking internal failure")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(exc))
            return booking_pb2.BookingResponse()

        return booking_pb2.BookingResponse(
            id=booking["id"],
            user_id=booking["user_id"],
            hotel_id=booking["hotel_id"],
            promo_code=booking["promo_code"],
            discount_percent=booking["discount_percent"],
            price=booking["price"],
            created_at=booking["created_at"],
        )

    async def ListBookings(
        self,
        request: booking_pb2.BookingListRequest,
        context: grpc.aio.ServicerContext,
    ) -> booking_pb2.BookingListResponse:
        """Обрабатывает запрос списка бронирований пользователя.

        Args:
            request: Запрос с идентификатором пользователя.
            context: Контекст gRPC-вызова.

        Returns:
            BookingListResponse: Список бронирований пользователя.
        """
        logging.info("ListBookings user=%s", request.user_id)
        bookings = await self.service.list_bookings(user_id=request.user_id)
        return booking_pb2.BookingListResponse(
            bookings=[booking_pb2.BookingResponse(**b) for b in bookings],
        )
