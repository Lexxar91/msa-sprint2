IMAGE_NAME?=booking-service-task5
IMAGE_TAG?=task5
ISTIOCTL?=istioctl

build:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG)-v1 -t $(IMAGE_NAME):$(IMAGE_TAG)-v2 ./booking-service

test:
	./test-service.sh $(IMAGE_NAME):$(IMAGE_TAG)-v2

load-to-minikube: build
	minikube image load $(IMAGE_NAME):$(IMAGE_TAG)-v1 $(IMAGE_NAME):$(IMAGE_TAG)-v2

setup-istio:
	ISTIOCTL=$(ISTIOCTL) ./setup-istio.sh

deploy:
	helm upgrade --install booking-service-v1 ./helm/booking-service -f results/values-v1.yaml --set image.name=$(IMAGE_NAME) --set-string image.tag=$(IMAGE_TAG)-v1 -n default --wait --timeout 180s
	helm upgrade --install booking-service-v2 ./helm/booking-service -f results/values-v2.yaml --set image.name=$(IMAGE_NAME) --set-string image.tag=$(IMAGE_TAG)-v2 -n default --wait --timeout 180s
	kubectl apply -f results/gateway.yaml -f results/destination-rule.yaml -f results/virtual-service.yaml -f results/envoy-filter.yaml
	kubectl patch deployment istio-ingressgateway -n istio-system --type=merge --patch-file results/gateway-stats-patch.yaml
	kubectl rollout status deployment/istio-ingressgateway -n istio-system --timeout=180s

status:
	./check-status.sh default

check-dns:
	./check-dns.sh default

port-forward:
	kubectl port-forward -n istio-system svc/istio-ingressgateway 9090:80

check:
	./check-istio.sh
	./check-canary.sh
	./check-feature-flag.sh
	./check-fallback.sh

.PHONY: build test load-to-minikube setup-istio deploy status check-dns port-forward check
