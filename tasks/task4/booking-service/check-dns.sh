#!/bin/bash

echo "▶️ Running in-cluster DNS test..."

kubectl run dns-test --rm -it \
  --image=busybox:1.36 \
  --restart=Never \
  --namespace=staging \
  -- \
  wget -qO- --timeout=5 http://booking-service/ping

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ Success: DNS работает, booking-service доступен по имени"
  exit 0
else
  echo ""
  echo "❌ Failed: не удалось обратиться к booking-service"
  echo "Проверь:"
  echo "  1. kubectl get svc booking-service -n staging"
  echo "  2. kubectl get pods -l app=booking-service -n staging"
  exit 1
fi
