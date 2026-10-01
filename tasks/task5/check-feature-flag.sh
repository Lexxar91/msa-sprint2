#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${BASE_URL:-http://localhost:9090}
HOST=${HOST:-booking.task5.local}
for ((i = 0; i < 20; i++)); do
  [ "$(curl -fsS --max-time 12 -H "Host: $HOST" -H 'X-Feature-Enabled: true' "$BASE_URL/ping")" = 'pong v2' ]
done
[ "$(curl -fsS --max-time 12 -H "Host: $HOST" -H 'X-Feature-Enabled: true' "$BASE_URL/feature")" = 'Feature X is enabled!' ]
[ "$(curl -sS --max-time 12 -o /dev/null -w '%{http_code}' -H "Host: $HOST" "$BASE_URL/feature")" = 404 ]
[ "$(curl -sS --max-time 12 -o /dev/null -w '%{http_code}' -H "Host: $HOST" -H 'X-Feature-Enabled: false' "$BASE_URL/feature")" = 404 ]
[ "$(curl -sS --max-time 12 -o /dev/null -w '%{http_code}' -H "Host: $HOST" -H 'X-Task5-Version: v2' "$BASE_URL/feature")" = 404 ]
echo "Success: 20/20 запросов с флагом попали на v2; /feature включён только с X-Feature-Enabled: true"
