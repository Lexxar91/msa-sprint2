# Task4: отчёт о реализации

## Изменения

- Helm Deployment использует `image.name`, как задано в values. Настроены liveness/readiness по `/ping`, ресурсы и Service ClusterIP `80 → 8080`.
- Makefile загружает образ через `minikube image load` и использует один тег при сборке, проверке и деплое. Добавлена цель `make test`.
- Dockerfile собирает сервис на Go и документирует порт 8080. DNS проверяется с Ubuntu через kubectl; копировать этот скрипт в образ сервиса не требуется.
- Скрипты проверки исполняемые, останавливаются при ошибках и принимают namespace. DNS-проверка не требует TTY и проверяет ответ `pong`.
- `test-service.sh` проверяет `/ping`, HTTP 404 для выключенного флага и ответ `/feature` для включённого. Временные контейнеры удаляются через EXIT trap.
- GitHub Actions workflow расположен в `.github/workflows/task4.yml` в корне репозитория. Цепочка: `build → test → deploy → tag`.
- Между jobs передаётся архив одного собранного образа через artifacts; Docker Registry не используется. В deploy архив загружается в Minikube, затем выполняются Helm и проверки DNS.
- Git-тег с timestamp UTC публикуется только после успешного push в main. В PR тег не создаётся.
- README содержит команды локального запуска, проверки и сведения о staging/production.

## Окружения

Общие параметры находятся в `../helm/booking-service/values.yaml`. Файлы `values-staging.yaml` и `values-prod.yaml` в этой папке — копии настроек окружений.

- staging: одна реплика, `ENABLE_FEATURE_X=true`;
- production: три реплики, `ENABLE_FEATURE_X=false`.

Флаг читается при запуске сервиса. Изменение env через Helm обновляет поды. Один `/ping` используется как проверка жизни и готовности простого сервиса.

## Выполненные проверки

Локальная проверка проведена 1 октября 2026 года на Ubuntu, профиль Minikube `minikube`, namespace `staging`, образ `booking-service:task4-review`.

| Проверка | Результат | Подтверждение |
| --- | --- | --- |
| Docker build | Успешно | `build.log` |
| Smoke test, оба значения флага | Успешно | `test.log` |
| Helm lint, staging и production | Оба прошли | production: `helm-prod.log`; staging: вывод команды при проверке |
| Helm template | Корректный образ, реплики, флаг и пробы | `rendered-staging.yaml`, `rendered-prod.yaml` |
| Загрузка образа в Minikube | Успешно | `load-image.log` |
| Helm deploy staging | deployed, revision 1 | `deploy.log` |
| Поды, Service и EndpointSlice | Под Running, готовность 1/1, Service 80/TCP | `check-status.log` |
| DNS из временного пода | /ping вернул pong | `check-dns.log` |
| /ping через port-forward на localhost:18080 | pong | `curl-ping.log` |
| /feature через port-forward | Feature X is enabled! | `curl-feature.log` |
| Образы Docker и Minikube | Проверенный образ есть в обоих | `docker-images.log`, `minikube-images.log` |
| Синтаксис Bash | bash -n прошёл для трёх скриптов | Вывод ошибок отсутствовал |
| Workflow YAML | Успешно разобран, четыре jobs присутствуют | Проверка PyYAML |

Production-конфигурация проверена через lint/template; production-релиз не устанавливался. Временные тестовые контейнеры, DNS-под и port-forward удалены. Сервис оставлен работающим в staging.

## GitHub Actions и границы проверки

Workflow подготовлен, но на GitHub ещё не запускался; публикация git-тега не выполнялась. Локальные проверки подтверждают работу образа, Helm и DNS, но не заменяют запуск workflow на GitHub.

GitHub Actions создаёт временный Minikube на своём runner. Этот кластер удаляется после job и не обновляет Minikube на Ubuntu пользователя.

По выбору пользователя реализован GitHub Actions вместо требуемых в исходном задании `.gitlab-ci.yml` и gitlab-ci-local. Исходный GitLab-драфт не используется. Копия рабочего workflow для сдачи находится в `github-actions.yml`; исполняемый источник — `.github/workflows/task4.yml` в корне репозитория.
