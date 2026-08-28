import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { buildSubgraphSchema } from '@apollo/subgraph';
import gql from 'graphql-tag';

const typeDefs = gql`
  type Hotel @key(fields: "id") {
    id: ID!
    name: String
    city: String
    stars: Int
    address: String
  }

  extend type Booking @key(fields: "id") {
    id: ID! @external
    hotelId: String! @external
    hotel: Hotel @requires(fields: "hotelId")
  }
`;

const resolvers = {
Hotel: {
    __resolveReference: async (reference) => {
      return {
        id: reference.id,
        name: `Hotel ${reference.id}`,
        city: "Moscow",
        stars: 5,
        address: "Red Square, 1"
      };
    },
  },
  Booking: {
    hotel: async (booking) => {
      return {
        id: booking.hotelId,
        name: `Hotel ${booking.hotelId}`,
        city: "Moscow",
        stars: 5,
        address: "Red Square, 1"
      };
    },
  },
};

const server = new ApolloServer({
  schema: buildSubgraphSchema([{ typeDefs, resolvers }]),
});

startStandaloneServer(server, {
  listen: { port: 4002 },
}).then(() => {
  console.log('✅ Hotel subgraph ready at http://localhost:4002/');
});