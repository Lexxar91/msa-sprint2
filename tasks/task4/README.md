# Task4: Docker, Helm и GitHub Actions

## Окружение

Нужны Docker, Minikube, Helm, kubectl, make, Bash и curl. Go устанавливать на Ubuntu не нужно: сервис собирается внутри Docker.

```bash
minikube start --driver=docker
cd tasks/task4
```

## Сборка, тесты и деплой

```bash
IMAGE_TAG=$(date -u +%Y%m%d-%H%M%S)
make build test load-to-minikube deploy IMAGE_TAG="$IMAGE_TAG"
./check-status.sh staging
./check-dns.sh staging
```

`load-to-minikube` загружает образ в кластер. `deploy` использует тот же тег и `image.pullPolicy=Never`. Уникальный тег позволяет Kubernetes увидеть новую версию приложения.

Для проверки через localhost выполните в одном терминале:

```bash
kubectl port-forward svc/booking-service 8080:80 -n staging
```

В другом терминале:

```bash
curl -f http://localhost:8080/ping
curl -f http://localhost:8080/feature
```

Ожидается `pong` и `Feature X is enabled!`. DNS-имя `booking-service` доступно внутри namespace кластера, а port-forward даёт доступ с Ubuntu.

## Staging и production

Общие настройки находятся в `helm/booking-service/values.yaml`. Helm объединяет их с файлом выбранного окружения:

- staging: одна реплика, меньшие ресурсы, `ENABLE_FEATURE_X=true`;
- production: три реплики, больше ресурсов, `ENABLE_FEATURE_X=false`.

Локальное развёртывание production-конфигурации в том же Minikube:

```bash
make deploy-prod IMAGE_TAG="$IMAGE_TAG"
./check-status.sh production
./check-dns.sh production
```

Образ с этим тегом должен быть заранее загружен. В production `/feature` возвращает HTTP 404. Значение флага читается при запуске приложения; изменение через Helm создаёт новые поды.

## GitHub Actions

Пайплайн находится в корне репозитория: `.github/workflows/task4.yml`.

1. `build`: собирает Docker-образ с тегом SHA коммита и сохраняет архив как artifact.
2. `test`: загружает тот же образ, проверяет `/ping` и `/feature` с включённым и выключенным флагом. Временные контейнеры удаляются и при ошибках.
3. `deploy`: запускает временный Minikube на runner GitHub, проверяет Helm-чарт, загружает архив через `minikube image load`, выполняет `helm upgrade --install` и DNS-проверку.
4. `tag`: после успешного push в `main` создаёт и публикует git-тег с timestamp UTC.

Workflow запускается для изменений task4 при push/PR в `main`, а также вручную через Actions → Task4 CI/CD → Run workflow. В PR выполняются сборка, тесты и деплой, но тег не создаётся.

Деплой GitHub Actions происходит в отдельном временном кластере runner, который удаляется после задания. Он не обновляет Minikube на вашей Ubuntu. Для локального кластера используйте Makefile.

Docker Registry и registry-секреты не нужны: один собранный образ передаётся между заданиями архивом. GitLab и gitlab-ci-local не используются по выбранному варианту реализации. В исходном задании они явно требуются — это отличие от формальных требований сдачи.

## Результаты

В `results/` находятся отчёт, копии конфигураций и вывод локальных проверок. Код сервиса, Dockerfile и Helm-чарт находятся рядом в task4; актуальный workflow — в корне репозитория.
