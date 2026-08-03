#!/bin/bash
# Регрессия ПОСЛЕ миграции BookingService в микросервис (Task2).
# Монолит (REST :8084) проксирует POST /api/bookings в booking-service (gRPC :9090).
# Запуск из tasks/task2:  bash results/regress.sh | tee results/test-log.txt
set -uo pipefail
BASE="${BASE:-http://localhost:8084}"
PASS=0; FAIL=0
pass(){ echo "  [PASS] $1"; PASS=$((PASS+1)); }
fail(){ echo "  [FAIL] $1"; FAIL=$((FAIL+1)); }
echo "🏁 Регрессия после миграции (REST монолита -> gRPC booking-service)"

echo "== Фикстуры (идемпотентно, старая БД) =="
docker compose exec -T monolith-db psql -U hotelio -d hotelio -q -v ON_ERROR_STOP=1 -f - \
  < ../../test/init-fixtures.sql && pass "фикстуры в monolith-db" || fail "фикстуры"

echo "== Монолит: чтения, которые остались =="
curl -s "$BASE/api/users/test-user-2/active"        | grep -q true && pass "user active"      || fail "user active"
curl -s "$BASE/api/users/test-user-1/blacklisted"   | grep -q true && pass "user blacklisted" || fail "user blacklisted"
curl -s "$BASE/api/hotels/test-hotel-1/operational" | grep -q true && pass "hotel operational"|| fail "hotel operational"
curl -s "$BASE/api/hotels/test-hotel-2/fully-booked"| grep -q true && pass "hotel fully-booked"|| fail "hotel fully-booked"
curl -s "$BASE/api/reviews/hotel/test-hotel-1/trusted"| grep -q true && pass "hotel trusted"  || fail "hotel trusted"
curl -s "$BASE/api/promos/TESTCODE1"                | grep -q TESTCODE1 && pass "promo get"   || fail "promo get"

echo "== Бронирования: теперь через gRPC =="
before=$(docker compose exec -T booking-db psql -U booking -d booking -tAc "select count(*) from booking;")
curl -s -X POST "$BASE/api/bookings?userId=test-user-3&hotelId=test-hotel-1" | grep -q test-hotel-1 \
  && pass "бронь без промо (REST->gRPC)" || fail "бронь без промо"
curl -s -X POST "$BASE/api/bookings?userId=test-user-2&hotelId=test-hotel-1&promoCode=TESTCODE1" | grep -q TESTCODE1 \
  && pass "бронь с промо (REST->gRPC)" || fail "бронь с промо"
after=$(docker compose exec -T booking-db psql -U booking -d booking -tAc "select count(*) from booking;")
[ "$after" -gt "$before" ] && pass "запись в booking-db ($before -> $after)" || fail "нет записи в booking-db"

echo "== Негативные кейсы (бизнес-ошибка = не-2xx) =="
for c in "userId=test-user-0&hotelId=test-hotel-1:неактивный" \
         "userId=test-user-1&hotelId=test-hotel-1:ЧС" \
         "userId=test-user-2&hotelId=test-hotel-3:недоверенный" \
         "userId=test-user-2&hotelId=test-hotel-2:занят"; do
  p="${c%%:*}"; n="${c##*:}"
  code=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/bookings?$p")
  [ "$code" -ge 400 ] && pass "отклонено: $n (HTTP $code)" || fail "не отклонено: $n (HTTP $code)"
done

echo "== История (RabbitMQ -> history-db) =="
sleep 2
hist=$(docker compose exec -T history-db psql -U history -d history -tAc "select count(*) from booking_history;")
[ "$hist" -gt 0 ] && pass "история пишется (строк: $hist)" || fail "история пуста"

echo; echo "ИТОГ: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" -eq 0 ] && echo "✅ Все тесты пройдены" || echo "❌ Есть падения"
exit "$FAIL"