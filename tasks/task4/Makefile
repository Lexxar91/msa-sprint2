IMAGE_NAME?=booking-service
IMAGE_TAG?=latest
NAMESPACE?=staging
RELEASE_NAME?=booking-service
VALUES_FILE?=./helm/booking-service/values-staging.yaml


build:
	@echo "🔨 Building Docker image..."
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) ./booking-service
	@echo "✅ Image built: $(IMAGE_NAME):$(IMAGE_TAG)"

run: build
	@echo "🚀 Running container..."
	docker run -d --name $(IMAGE_NAME)-test -p 8080:8080 $(IMAGE_NAME):$(IMAGE_TAG)
	@echo "✅ Container running at http://localhost:8080/ping"

stop:
	@echo "🛑 Stopping container..."
	-docker rm -f $(IMAGE_NAME)-test
	@echo "✅ Container stopped"

test:
	./test-service.sh $(IMAGE_NAME):$(IMAGE_TAG)

load-to-minikube: build
	@echo "📦 Loading image into Minikube..."
	minikube image load $(IMAGE_NAME):$(IMAGE_TAG)
	@echo "✅ Image loaded into Minikube"

deploy:
	@echo "🚀 Deploying to $(NAMESPACE)..."
	helm upgrade --install $(RELEASE_NAME) ./helm/booking-service \
	    --set image.name=$(IMAGE_NAME) \
	    --set-string image.tag=$(IMAGE_TAG) \
	    --set image.pullPolicy=Never \
	    -f $(VALUES_FILE) \
	    -n $(NAMESPACE) \
	    --create-namespace \
	    --atomic
	@echo "✅ Deployed to $(NAMESPACE)"

deploy-prod:
	$(MAKE) deploy NAMESPACE=production VALUES_FILE=./helm/booking-service/values-prod.yaml

undeploy:
	@echo "🧹 Removing deployment..."
	helm uninstall $(RELEASE_NAME) -n $(NAMESPACE)
	@echo "✅ Deployment removed"

status:
	@echo "📊 Deployment status:"
	kubectl get pods -l app=$(RELEASE_NAME) -n $(NAMESPACE)
	@echo ""
	kubectl get svc $(RELEASE_NAME) -n $(NAMESPACE)

logs:
	kubectl logs -l app=$(RELEASE_NAME) -n $(NAMESPACE) -f --tail=100

check-dns:
	./check-dns.sh $(NAMESPACE) $(RELEASE_NAME)

clean: stop undeploy
	@echo "🧹 Cleaning up..."
	-docker rmi $(IMAGE_NAME):$(IMAGE_TAG)
	@echo "✅ Cleaned up"

help:
	@echo "Доступные команды:"
	@echo "  make build         - Собрать Docker-образ"
	@echo "  make test          - Проверить /ping и фича-флаг"
	@echo "  make run           - Запустить контейнер локально"
	@echo "  make stop          - Остановить контейнер"
	@echo "  make load-to-minikube - Загрузить образ в Minikube"
	@echo "  make deploy        - Деплой в staging через Helm"
	@echo "  make deploy-prod   - Деплой в production"
	@echo "  make undeploy      - Удалить деплой"
	@echo "  make status        - Статус деплоя"
	@echo "  make logs          - Логи приложения"
	@echo "  make check-dns     - Проверка DNS внутри кластера"
	@echo "  make clean         - Очистить всё"

.PHONY: build test run stop load-to-minikube deploy deploy-prod undeploy status logs check-dns clean help
