# Task5: Istio traffic management

## Результат

Task5 реализован и проверен локально в Minikube 1 октября 2026 года. Обе версии booking-service работают в namespace default; обе имеют готовность 2/2. Task4 остаётся отдельным приложением в staging.

Использована уже установленная mesh Istio 1.30.3 и соответствующий istioctl. Автоматическая инъекция в default была включена и проверена. `istioctl install --set profile=demo -y` дополнительно проверен в dry-run; существующая mesh повторно не устанавливалась. Для нового окружения эта команда предусмотрена в `../setup-istio.sh`.

## Реализация и причины решений

### Две версии сервиса

Dockerfile, сервис, Helm-чарт и локальные команды взяты из task4. Образ собирается один раз с тегами `task5-v1` и `task5-v2`; поведение версии задаётся через SERVICE_VERSION и ENABLE_FEATURE_X.

Helm устанавливает два Deployment: booking-service-v1 и booking-service-v2. Они имеют общую метку app=booking-service и отдельные метки version. Общий Service создаётся релизом v1; релиз v2 повторно его не создаёт. DestinationRule выбирает версии через subsets.

`/ping` возвращает `pong v1` или `pong v2`, а заголовок ответа X-Service-Version позволяет определить версию. В v2 функция доступна только при ENABLE_FEATURE_X=true и X-Feature-Enabled: true в запросе. Без заголовка `/feature` возвращает 404.

### Маршрутизация и фича-флаг

Gateway принимает Host booking.task5.local через существующий istio-ingressgateway. VirtualService распределяет обычные запросы: 90% на v1, 10% на v2.

Lua в EnvoyFilter читает X-Feature-Enabled и устанавливает внутренний заголовок x-task5-version=v2. Приоритетный маршрут VirtualService выбирает v2. Переданный клиентом внутренний заголовок удаляется, поэтому сам по себе он не включает функцию.

EnvoyFilter действует на ingressgateway и обрабатывает только Host booking.task5.local. Для проверки используется port-forward к gateway; прямой port-forward к Service обходит эту логику.

### Retry, circuit breaker и fallback

HTTP retry находится в VirtualService: две дополнительные попытки, по 2 секунды, при 5xx и ошибках соединения. В DestinationRule заданы лимиты соединений/запросов и maxRetries=10 — бюджет одновременных retries. Число попыток задаётся отдельно в VirtualService.

Outlier detection исключает endpoint после трёх последовательных 5xx, на базовый срок 10 секунд. Для проверки включены дополнительные счётчики Envoy через patch аннотации gateway: `gateway-stats-patch.yaml`. Применение этого patch вызвало перезапуск ingressgateway; его готовность была подтверждена.

Retry работает внутри выбранного subset и сам по себе не переключает v1 на v2. Явный fallback реализован в EnvoyFilter: после окончательного 5xx на GET /ping Lua делает HTTP-вызов subset v2 и заменяет ответ при успехе. В ответ добавляется X-Task5-Fallback: v2.

Fallback ограничен безопасным GET /ping. HTTP 4xx, другие пути и изменяющие данные операции не перенаправляются. Если v2 тоже отвечает ошибкой, исходная ошибка сохраняется. Запросы с фича-флагом, уже направленные на v2, не запускают fallback.

Для воспроизводимой проверки добавлен диагностический заголовок X-Demo-Failure: true: v1 отвечает 503 на /ping, а v2 работает. Обычные health/readiness-пробы не используют этот заголовок.

## Фактические проверки

| Проверка | Результат | Подтверждение |
| --- | --- | --- |
| Docker build | Успешно, два тега одного образа | build.log |
| Проверка фича-флага в контейнере | Оба значения env проверены, без заголовка функция отключена | test-service.log |
| Helm lint/template v1 и v2 | Успешно | helm-v1.log, helm-v2.log, rendered-v1.yaml, rendered-v2.yaml |
| Istio analyze | No validation issues found | istio-analyze.log |
| Установка приложения и правил | Оба Helm-релиза deployed | deploy.log |
| Инъекция и готовность | v1 и v2 готовы, istio-proxy присутствует | check-istio.log |
| Статус и DNS | Service 80/TCP, запрос из другого пода успешен | status-dns.log |
| Canary | Из 1000 запросов: v1=901 (90.1%), v2=99 (9.9%) | check-canary.log |
| Фича-заголовок | 20/20 запросов на v2; /feature включён только с true | check-feature-flag.log |
| Ошибка HTTP 503 в v1 | Ответ v2 после двух retries; одна enforced ejection | check-fallback.log |
| Полная остановка v1 | Все 20 запросов обслужила v2; 19 через явный fallback | check-fallback.log |
| Восстановление v1 | Исходная одна реплика восстановлена через EXIT trap | check-fallback.log, final-status.log |
| Запрос через gateway | HTTP 200, X-Service-Version=v2, X-Feature-Enabled=true | curl-feature-ping.log |
| Bash и изменения tracked-файлов | bash -n и git diff --check прошли | Проверено локальными командами |

В этой версии Kubernetes Envoy работает как native sidecar в initContainers с restartPolicy=Always. Проверка учитывает и обычное, и такое размещение прокси.

Canary вероятностный: веса 90/10 не означают ровно 90 и 10 ответов в каждой сотне. Скрипт проверяет выборку из 1000 запросов с диапазоном 5–15% для v2.

Для проверки отказа v1 масштабируется до нуля вместо удаления одного пода: Deployment автоматически заменил бы удалённый под. Скрипт сохраняет исходное число реплик и восстанавливает его при завершении, в том числе при ошибке.

После проверок v1 и v2 оставлены работающими. Временные контейнеры, DNS-под и port-forward удалены. Изменения не публиковались в GitHub, workflow task4 не изменялся.

## Переключение по заголовку

Заголовок — дополнительная информация в HTTP-запросе. X-Feature-Enabled: true означает: «для этого запроса нужна новая функция». Envoy отправляет такой запрос на v2 независимо от обычного распределения 90/10; приложение разрешает функцию именно этому запросу.

Таким образом, ENABLE_FEATURE_X разрешает функцию в запущенной версии приложения, а X-Feature-Enabled выбирает её для конкретного запроса.

## Документация

- [HTTP retry в VirtualService](https://istio.io/latest/docs/reference/config/networking/virtual-service/#HTTPRetry).
- [Outlier detection в DestinationRule](https://istio.io/latest/docs/reference/config/networking/destination-rule/#OutlierDetection).
- [Envoy Lua: заголовки, HTTP-вызовы и изменение ответа](https://www.envoyproxy.io/docs/envoy/latest/configuration/http/http_filters/lua_filter).
- [Дополнительные счётчики Envoy](https://istio.io/latest/docs/ops/configuration/telemetry/envoy-stats/).

Команды повторного развёртывания и проверок находятся в `../README.md`.
