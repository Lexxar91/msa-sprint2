import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "proto"))

import grpc
import booking_pb2
import booking_pb2_grpc

CASES = [
    ("happy path",      "test-user-2", "test-hotel-1", "TESTCODE1"),   # -> price 90.0
    ("VIP no promo",    "test-user-3", "test-hotel-1", ""),            # -> price 80.0
    ("inactive user",   "test-user-0", "test-hotel-1", "TESTCODE1"),   # -> INVALID_ARGUMENT
    ("blacklisted",     "test-user-1", "test-hotel-1", "TESTCODE1"),   # -> INVALID_ARGUMENT
    ("fully booked",    "test-user-2", "test-hotel-2", "TESTCODE1"),   # -> INVALID_ARGUMENT
    ("bad promo (ok)",  "test-user-2", "test-hotel-1", "TESTCODE-OLD"),# -> скидка 0, бронь проходит
]

def main() -> None:
    with grpc.insecure_channel("localhost:9090") as channel:
        stub = booking_pb2_grpc.BookingServiceStub(channel)
        for name, uid, hid, promo in CASES:
            try:
                r = stub.CreateBooking(booking_pb2.BookingRequest(
                    user_id=uid, hotel_id=hid, promo_code=promo))
                print(f"[OK]   {name:16} -> price={r.price}, discount={r.discount_percent}")
            except grpc.RpcError as e:
                print(f"[FAIL] {name:16} -> {e.code().name}: {e.details()}")

if __name__ == "__main__":
    main()