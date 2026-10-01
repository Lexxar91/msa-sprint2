#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${1:-default}

echo "Поды в namespace '$NAMESPACE':"
kubectl get pods -l app=booking-service -n "$NAMESPACE"
echo "Service:"
kubectl get svc booking-service -n "$NAMESPACE"
echo "Endpoints:"
kubectl get endpointslices -l kubernetes.io/service-name=booking-service -n "$NAMESPACE"
echo "Для локального теста:"
echo "kubectl port-forward svc/booking-service 8080:80 -n $NAMESPACE"
echo "curl http://localhost:8080/ping"
