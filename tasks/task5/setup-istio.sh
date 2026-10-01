#!/usr/bin/env bash
set -euo pipefail

ISTIOCTL=${ISTIOCTL:-istioctl}
if kubectl get deployment istiod -n istio-system >/dev/null 2>&1; then
  echo "Istio уже установлен; используем существующую mesh"
  "$ISTIOCTL" version
else
  "$ISTIOCTL" install --set profile=demo -y
fi
kubectl label namespace default istio-injection=enabled --overwrite
