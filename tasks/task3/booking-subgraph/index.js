import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { buildSubgraphSchema } from '@apollo/subgraph';
import gql from 'graphql-tag';
import { BookingServiceClient } from './booking_grpc_pb.cjs';
import pkg from './booking_pb.cjs';
import { credentials } from '@grpc/grpc-js';

const { BookingListRequest } = pkg;

const client = new BookingServiceClient('booking-service:9090', credentials.createInsecure());

const typeDefs = gql`
  type Booking @key(fields: "id") {
    id: ID!
    userId: String!
    hotelId: String!
    promoCode: String
    discountPercent: Int
  }

  type Query {
    bookingsByUser(userId: String!): [Booking]
  }
`;

const resolvers = {
  Query: {
    /**
     * Возвращает бронирования пользователя после проверки заголовка userid.
     * @param {*} _ Родительское значение GraphQL.
     * @param {*} options2 Параметры вызова.
     * @param {*} options3 Параметры вызова.
     * @returns {*} Результат обработки вызова.
     */
    bookingsByUser: async (_, { userId }, { req }) => {
      const headerUserId = req.headers['userid'];
      if (!headerUserId) {
        throw new Error('Unauthorized: missing userid header');
      }
      if (headerUserId !== userId) {
        throw new Error('Forbidden: you can only view your own bookings');
      }
      const request = new BookingListRequest();
      request.setUserId(userId);
      return new Promise(
        /**
         * Запрашивает бронирования через gRPC-клиент.
         * @param {*} resolve Завершение Promise с результатом.
         * @param {*} reject Завершение Promise с ошибкой.
         * @returns {*} Результат обработки вызова.
         */
        (resolve, reject) => {
          client.listBookings(
            request,
            /**
             * Преобразует gRPC-ответ в список GraphQL-бронирований.
             * @param {*} err Ошибка gRPC-вызова.
             * @param {*} response Ответ gRPC-сервиса.
             * @returns {*} Результат обработки вызова.
             */
            (err, response) => {
              if (err) {
                console.error('gRPC error:', err);
                reject(new Error('Failed to fetch bookings'));
              }
              const bookings = response.getBookingsList().map(
                /**
                 * Преобразует protobuf-бронирование в объект GraphQL.
                 * @param {*} b Protobuf-бронирование.
                 * @returns {*} Результат обработки вызова.
                 */
                (b) => ({
                  id: b.getId(),
                  userId: b.getUserId(),
                  hotelId: b.getHotelId(),
                  promoCode: b.getPromoCode(),
                  discountPercent: b.getDiscountPercent(),
                }),
              );
              resolve(bookings);
            },
          );
        },
      );
    },
  },

  Booking: {
    /**
     * Возвращает ссылку на бронирование для Федерации.
     * @param {*} reference Ссылка Федерации с идентификатором.
     * @returns {*} Результат обработки вызова.
     */
    __resolveReference: async (reference) => {
      return { id: reference.id };
    },
  },
};

const server = new ApolloServer({
  schema: buildSubgraphSchema([{ typeDefs, resolvers }]),
});

startStandaloneServer(server, {
  listen: { port: 4001 },

  /**
   * Передаёт HTTP-запрос в контекст GraphQL.
   * @param {*} options1 Параметры вызова.
   * @returns {*} Результат обработки вызова.
   */
  context: async ({ req }) => ({ req }),
}).then(
  /**
   * Сообщает о запуске GraphQL-сервера.
   * @returns {*} Результат обработки вызова.
   */
  () => {
    console.log('✅ Booking subgraph ready at http://localhost:4001/');
  },
);
