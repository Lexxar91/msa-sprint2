# Проверка task2 перед сдачей

Дата: 1 октября 2026 года. Текущая подготовка добавляет документацию и форматирование, сохраняет бизнес-логику и зависимости.

Все сервисы общего Docker-стенда успешно собраны. Существующий `tasks/task2/regress.sh` выполнен на отдельном проекте `hotelio-review` с временными базами: **PASS=15, FAIL=0**. Проверены справочники монолита, создание бронирований REST → gRPC, отрицательные бизнес-сценарии, сохранение бронирований и доставка `BookingCreated` в историю. Отрицательные сценарии возвращают HTTP 500 в существующем REST-прокси; скрипт проверяет статус не ниже 400.

Артефакты:

- [submission-regression.log](submission-regression.log) — вывод регрессии.
- [submission-docker-ps.log](submission-docker-ps.log) — состояния контейнеров.
- [submission-services.log](submission-services.log) — обработка запросов и событий.
- [submission-history.log](submission-history.log) — две записи в истории после регрессии.

Исходники и Dockerfile сервисов: [booking-service](../booking-service) и [booking-history-service](../booking-history-service). Сгенерированные protobuf-модули сохранены без правок.

Проект использует RabbitMQ, хотя исходное задание требует Kafka. Это существующее архитектурное отклонение описано в [ADR](../../task1/results/ADR.md); успешная регрессия не устраняет формальное расхождение.
