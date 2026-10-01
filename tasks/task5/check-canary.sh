#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${BASE_URL:-http://localhost:9090}
HOST=${HOST:-booking.task5.local}
REQUESTS=${REQUESTS:-1000}
[[ "$REQUESTS" =~ ^[0-9]+$ ]] && [ "$REQUESTS" -ge 100 ]
v1=0
v2=0
for ((i = 0; i < REQUESTS; i++)); do
  response=$(curl -fsS --max-time 12 -H "Host: $HOST" "$BASE_URL/ping")
  case "$response" in
    'pong v1') v1=$((v1 + 1)) ;;
    'pong v2') v2=$((v2 + 1)) ;;
    *)
      echo "Ошибка: неожиданный ответ: $response" >&2
      exit 1
      ;;
  esac
done
awk -v v1="$v1" -v v2="$v2" -v n="$REQUESTS" 'BEGIN {printf "Запросов: %d; v1: %d (%.1f%%); v2: %d (%.1f%%)\n", n, v1, 100*v1/n, v2, 100*v2/n}'
[ "$((v2 * 100))" -ge "$((REQUESTS * 5))" ]
[ "$((v2 * 100))" -le "$((REQUESTS * 15))" ]
echo "Success: canary соответствует весам 90/10 с допуском выборки"
