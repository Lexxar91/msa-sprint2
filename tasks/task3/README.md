# Task 3 — GraphQL Federation (Apollo Gateway)

Построение единого GraphQL API поверх двух субграфов (booking и hotel) с помощью Apollo Federation. Gateway объединяет схемы субграфов в один суперграф, позволяя клиенту запрашивать данные из разных сервисов одним запросом.

## Архитектура

```
                    ┌─────────────────────┐
                    │   Apollo Gateway     │
                    │   (port 4000)        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                                 ▼
   ┌─────────────────────┐          ┌─────────────────────┐
   │  Booking Subgraph    │          │  Hotel Subgraph      │
   │  (port 4001)         │          │  (port 4002)         │
   └──────────┬──────────┘          └─────────────────────┘
              │
              ▼
   ┌─────────────────────┐
   │  Booking Service     │
   │  gRPC (port 9090)    │
   │  (Task 2)            │
   └─────────────────────┘
```

### Компоненты

| Сервис              | Порт | Описание                                                      |
|---------------------|------|---------------------------------------------------------------|
| `apollo-gateway`    | 4000 | Apollo Gateway — единая точка входа для GraphQL-клиентов     |
| `booking-subgraph`  | 4001 | Субграф бронирований; вызывает booking-service через gRPC    |
| `hotel-subgraph`    | 4002 | Субграф отелей; резолвит поле `hotel` на типе `Booking`      |

## Структура директории

```
task3/
├── gateway/
│   ├── index.js          # Конфигурация Apollo Gateway
│   ├── package.json
│   └── Dockerfile
├── booking-subgraph/
│   ├── index.js          # GraphQL-схема + gRPC-клиент к booking-service
│   ├── booking_pb.cjs    # Сгенерированные protobuf-сообщения
│   ├── booking_grpc_pb.cjs  # Сгенерированный gRPC-клиент
│   ├── package.json
│   └── Dockerfile
├── hotel-subgraph/
│   ├── index.js          # GraphQL-схема + резолвер hotel на Booking
│   ├── package.json
│   └── Dockerfile
└── README.md
```

## Что реализовано

### Apollo Gateway

- Объединяет схемы `booking` и `hotel` субграфов в единый суперграф.
- Автоматически пробрасывает HTTP-заголовок `userid` из клиентского запроса во все субграфы через `willSendRequest` в `RemoteGraphQLDataSource`.
- Слушает на порту `4000`.

### Booking Subgraph

- Владелец типа `Booking` (`@key(fields: "id")`).
- Предоставляет query `bookingsByUser(userId: String!): [Booking]`.
- Внутри резолвера вызывает gRPC-метод `ListBookings` из booking-service (Task 2) и преобразует protobuf-ответ в GraphQL-формат.
- Реализует `__resolveReference` для Federation — возвращает сущность Booking по ключу `id`.
- **ACL**: проверяет, что заголовок `userid` присутствует и совпадает с запрашиваемым `userId`. Если нет — бросает `Unauthorized` / `Forbidden`.

### Hotel Subgraph

- Владелец типа `Hotel` (`@key(fields: "id")`).
- Расширяет тип `Booking` (`extend type Booking`) полем `hotel: Hotel`.
- Использует `@external` + `@requires(fields: "hotelId")`, чтобы получить `hotelId` из booking-subgraph и разрешить отель.
- Резолвер `Booking.hotel` возвращает данные отеля по `hotelId`. В текущей реализации — заглушка (mock); в продакшене заменяется на REST-вызов к монолиту (`GET /api/hotels/{hotelId}`).

### GraphQL-схема (суперграф)

```graphql
type Booking {
  id: ID!
  userId: String!
  hotelId: String!
  promoCode: String
  discountPercent: Int
  hotel: Hotel              # резолвится hotel-subgraph
}

type Hotel {
  id: ID!
  name: String
  city: String
  stars: Int
  address: String
}

type Query {
  bookingsByUser(userId: String!): [Booking]
}
```

### Межсервисное взаимодействие

- **Gateway → Subgraphs**: HTTP/GraphQL (Apollo Federation).
- **Booking Subgraph → Booking Service**: gRPC (`booking-service:9090`), protobuf-сообщения `BookingListRequest` / `BookingListResponse`.
- **Заголовки**: Gateway пробрасывает `userid` во все подграфы для проверки ACL.

## Запуск

### Предварительные требования

Task 3 работает поверх сервисов из Task 1 и Task 2 (монолит, booking-service, базы данных). Все сервисы определены в общем `tasks/docker-compose.yml`.

### Поднятие

```bash
cd tasks
docker compose up -d --build
```

Gateway будет доступен по адресу: `http://localhost:4000/`

### Проверка

#### 1. Создание тестовых бронирований

Перед запросами через gateway нужно создать бронирования в booking-service. Запустите gRPC-тестовый клиент внутри контейнера:

```bash
docker compose exec booking-service python test_client.py
```

Ожидаемый вывод:

```
[OK]   happy path       -> price=90.0, discount=10.0
[OK]   VIP no promo     -> price=80.0, discount=0.0
[FAIL] inactive user    -> INVALID_ARGUMENT: User is inactive
[FAIL] blacklisted      -> INVALID_ARGUMENT: User is blacklisted
[FAIL] fully booked     -> INVALID_ARGUMENT: Hotel is not trusted based on reviews
[OK]   bad promo (ok)   -> price=100.0, discount=0.0
```

#### 2. GraphQL-запрос через Gateway

```bash
curl -X POST http://localhost:4000/ \
  -H "Content-Type: application/json" \
  -H "userid: test-user-2" \
  -d '{
    "query": "query { bookingsByUser(userId: \"test-user-2\") { id hotelId hotel { id name city stars } discountPercent } }"
  }'
```

Ожидаемый ответ:

```json
{
  "data": {
    "bookingsByUser": [
      {
        "id": "1",
        "hotelId": "test-hotel-1",
        "hotel": {
          "id": "test-hotel-1",
          "name": "Hotel test-hotel-1",
          "city": "Moscow",
          "stars": 5
        },
        "discountPercent": 10
      },
      {
        "id": "3",
        "hotelId": "test-hotel-1",
        "hotel": {
          "id": "test-hotel-1",
          "name": "Hotel test-hotel-1",
          "city": "Moscow",
          "stars": 5
        },
        "discountPercent": 0
      }
    ]
  }
}
```

#### 3. Проверка ACL

Запрос без заголовка `userid` вернёт ошибку:

```bash
curl -X POST http://localhost:4000/ \
  -H "Content-Type: application/json" \
  -d '{"query": "query { bookingsByUser(userId: \"test-user-2\") { id } }"}'
```

```json
{
  "errors": [
    { "message": "Unauthorized: missing userid header" }
  ]
}
```

Запрос с несовпадающим `userid`:

```bash
curl -X POST http://localhost:4000/ \
  -H "Content-Type: application/json" \
  -H "userid: another-user" \
  -d '{"query": "query { bookingsByUser(userId: \"test-user-2\") { id } }"}'
```

```json
{
  "errors": [
    { "message": "Forbidden: you can only view your own bookings" }
  ]
}
```

## Технологии

- **[Apollo Gateway](https://www.apollographql.com/docs/federation/)** — Federation v2, композиция суперграфа
- **[Apollo Server](https://www.apollographql.com/docs/apollo-server/)** v4 — standalone-серверы для субграфов
- **[@apollo/subgraph](https://www.apollographql.com/docs/federation/v2/building-supergraphs/)** — директивы `@key`, `@external`, `@requires`
- **[gRPC](https://grpc.io/)** (`@grpc/grpc-js`) — связь booking-subgraph с booking-service
- **[Protobuf](https://developers.google.com/protocol-buffers)** — сериализация gRPC-сообщений
- **Node.js 18** — среда выполнения
- **Docker Compose** — оркестрация контейнеров, общая сеть `hotelio-net`
