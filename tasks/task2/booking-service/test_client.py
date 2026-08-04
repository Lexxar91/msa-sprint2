"""Тестовый клиент для проверки BookingService через gRPC."""

import os
import sys

import grpc

sys.path.append(os.path.join(os.path.dirname(__file__), "proto"))
import booking_pb2  # noqa: E402
import booking_pb2_grpc  # noqa: E402

CASES: list[tuple[str, str, str, str]] = [
    ("happy path",      "test-user-2", "test-hotel-1", "TESTCODE1"),    # price 90.0
    ("VIP no promo",    "test-user-3", "test-hotel-1", ""),             # price 80.0
    ("inactive user",   "test-user-0", "test-hotel-1", "TESTCODE1"),    # INVALID_ARGUMENT
    ("blacklisted",     "test-user-1", "test-hotel-1", "TESTCODE1"),    # INVALID_ARGUMENT
    ("fully booked",    "test-user-2", "test-hotel-2", "TESTCODE1"),    # INVALID_ARGUMENT
    ("bad promo (ok)",  "test-user-2", "test-hotel-1", "TESTCODE-OLD"), # скидка 0, бронь проходит
]


def main() -> None:
    """Подключается к gRPC-серверу и выполняет тестовые сценарии бронирования."""
    with grpc.insecure_channel("localhost:9090") as channel:
        stub = booking_pb2_grpc.BookingServiceStub(channel)
        for name, uid, hid, promo in CASES:
            try:
                response = stub.CreateBooking(booking_pb2.BookingRequest(
                    user_id=uid, hotel_id=hid, promo_code=promo,
                ))
                print(
                    f"[OK]   {name:16} -> price={response.price}, "
                    f"discount={response.discount_percent}",
                )
            except grpc.RpcError as exc:
                print(f"[FAIL] {name:16} -> {exc.code().name}: {exc.details()}")


if __name__ == "__main__":
    main()