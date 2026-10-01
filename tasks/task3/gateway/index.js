import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { ApolloGateway, RemoteGraphQLDataSource } from '@apollo/gateway';

const gateway = new ApolloGateway({
  serviceList: [
    { name: 'booking', url: 'http://booking-subgraph:4001' },
    { name: 'hotel', url: 'http://hotel-subgraph:4002' },
  ],

  /**
   * Создаёт клиент подграфа с передачей заголовка userid.
   * @param {*} options1 Параметры вызова.
   * @returns {*} Результат обработки вызова.
   */
  buildService: ({ url }) =>
    new RemoteGraphQLDataSource({
      url,

      /**
       * Передаёт идентификатор пользователя в запрос подграфа.
       * @param {*} options1 Параметры вызова.
       * @returns {*} Результат обработки вызова.
       */
      willSendRequest({ request, context }) {
        const userId = context?.req?.headers?.['userid'];
        if (userId) {
          request.http.headers.set('userid', userId);
        }
      },
    }),
});

const server = new ApolloServer({
  gateway,
  subscriptions: false,
});

startStandaloneServer(server, {
  listen: { port: 4000 },

  /**
   * Передаёт HTTP-запрос в контекст GraphQL.
   * @param {*} options1 Параметры вызова.
   * @returns {*} Результат обработки вызова.
   */
  context: async ({ req }) => ({ req }),
}).then(
  /**
   * Сообщает о запуске GraphQL-сервера.
   * @param {*} options1 Параметры вызова.
   * @returns {*} Результат обработки вызова.
   */
  ({ url }) => {
    console.log(`🚀 Gateway ready at ${url}`);
  },
);
