#!/usr/bin/env bash
set -euo pipefail

kubectl get pods -n istio-system
[ "$(kubectl get namespace default -o jsonpath='{.metadata.labels.istio-injection}')" = enabled ]
for version in v1 v2; do
  kubectl rollout status "deployment/booking-service-$version" -n default --timeout=120s
  kubectl get pods -n default -l "app=booking-service,version=$version" -o json |
    jq -e '.items | length > 0 and all(.[];
            any((.spec.containers + (.spec.initContainers // []))[]; .name == "istio-proxy")
            and all(.status.containerStatuses[]; .ready)
            and any((.status.containerStatuses + (.status.initContainerStatuses // []))[];
                .name == "istio-proxy" and .ready))' >/dev/null
done
kubectl get pods -n default -l app=booking-service
echo "Success: default injection=enabled, v1 и v2 готовы с istio-proxy"
