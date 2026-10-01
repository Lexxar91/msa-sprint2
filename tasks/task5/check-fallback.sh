#!/usr/bin/env bash
set -euo pipefail

BASE_URL=${BASE_URL:-http://localhost:9090}
HOST=${HOST:-booking.task5.local}
headers_file=$(mktemp)
replicas=$(kubectl get deployment booking-service-v1 -n default -o jsonpath='{.spec.replicas}')
restore_needed=false
## Удаляет временные ресурсы проверки.
cleanup() {
  rm -f "$headers_file"
  if [ "$restore_needed" = true ]; then
    kubectl scale deployment booking-service-v1 -n default --replicas="$replicas"
    kubectl rollout status deployment/booking-service-v1 -n default --timeout=120s
  fi
}
trap cleanup EXIT

## Читает статистику Envoy на ingress gateway.
stats() {
  kubectl exec -n istio-system deploy/istio-ingressgateway -- pilot-agent request GET 'stats?filter=booking.*(upstream_rq_retry|ejections_enforced_total)' 2>/dev/null
}
## Возвращает значение счётчика; $1 — имя метрики.
count_metric() {
  awk -v metric="$1" '$1 ~ metric {sum += $2} END {print sum+0}'
}
before=$(stats)
response=$(curl -fsS --max-time 12 -D "$headers_file" -H "Host: $HOST" -H 'X-Demo-Failure: true' "$BASE_URL/ping")
[ "$response" = 'pong v2' ]
grep -qi '^x-task5-fallback: v2' "$headers_file"
after=$(stats)
retry_before=$(printf '%s\n' "$before" | count_metric '[.]upstream_rq_retry:$')
retry_after=$(printf '%s\n' "$after" | count_metric '[.]upstream_rq_retry:$')
ejection_before=$(printf '%s\n' "$before" | count_metric '[.]ejections_enforced_total:$')
ejection_after=$(printf '%s\n' "$after" | count_metric '[.]ejections_enforced_total:$')
printf '%s\n' "$after"
[ "$retry_after" -gt "$retry_before" ]
[ "$ejection_after" -gt "$ejection_before" ]
echo "Success: HTTP 503 от v1 вызвал retries, circuit breaker и fallback на v2"

restore_needed=true
kubectl scale deployment booking-service-v1 -n default --replicas=0
kubectl wait --for=delete pod -n default -l app=booking-service,version=v1 --timeout=120s
fallback_count=0
for ((i = 0; i < 20; i++)); do
  response=$(curl -fsS --max-time 12 -D "$headers_file" -H "Host: $HOST" "$BASE_URL/ping")
  [ "$response" = 'pong v2' ]
  if grep -qi '^x-task5-fallback: v2' "$headers_file"; then
    fallback_count=$((fallback_count + 1))
  fi
done
[ "$fallback_count" -gt 0 ]
echo "Success: при остановленной v1 все 20 запросов обслужила v2; fallback сработал $fallback_count раз"
