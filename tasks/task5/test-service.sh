#!/usr/bin/env bash
set -euo pipefail

IMAGE=${1:-booking-service-task5:task5-v1}
CONTAINER_NAME="booking-service-test-$$"

## Удаляет временные ресурсы проверки.
cleanup() {
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
}
trap cleanup EXIT

for feature_enabled in false true; do
  docker run -d --name "$CONTAINER_NAME" -p 127.0.0.1::8080 \
    -e SERVICE_VERSION=v2 -e ENABLE_FEATURE_X="$feature_enabled" "$IMAGE" >/dev/null
  address=$(docker port "$CONTAINER_NAME" 8080/tcp)
  ready=false
  for attempt in {1..30}; do
    if [ "$(curl -fsS --max-time 2 "http://$address/ping" 2>/dev/null || true)" = "pong v2" ]; then
      ready=true
      break
    fi
    sleep 1
  done
  if [ "$ready" != true ]; then
    docker logs "$CONTAINER_NAME"
    echo "Ошибка: /ping не вернул pong" >&2
    exit 1
  fi
  [ "$(curl -sS --max-time 5 -o /dev/null -w '%{http_code}' "http://$address/feature")" = 404 ]
  if [ "$feature_enabled" = true ]; then
    [ "$(curl -fsS --max-time 5 -H "X-Feature-Enabled: true" "http://$address/feature")" = 'Feature X is enabled!' ]
  else
    [ "$(curl -sS --max-time 5 -H "X-Feature-Enabled: true" -o /dev/null -w '%{http_code}' "http://$address/feature")" = 404 ]
  fi
  echo "Success: /ping=pong v2, ENABLE_FEATURE_X=$feature_enabled проверен"
  cleanup
done
