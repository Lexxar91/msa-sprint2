#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${1:-default}
SERVICE_NAME=${2:-booking-service}
POD_NAME="dns-test-$(date +%s)-$$"

echo "Проверка DNS в namespace '$NAMESPACE'..."
kubectl run "$POD_NAME" --rm -i --attach=true \
  --image=busybox:1.36 \
  --restart=Never \
  --namespace="$NAMESPACE" \
  --pod-running-timeout=120s \
  -- sh -c 'response=$(wget -qO- -T 5 "$1") && case "$response" in "pong v1"|"pong v2") true ;; *) exit 1 ;; esac && printf "%s\n" "$response"' \
  sh "http://$SERVICE_NAME/ping"
echo "Success: DNS работает, /ping вернул pong с версией"
