// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('@grpc/grpc-js');
var booking_pb = require('./booking_pb.cjs');

function serialize_booking_BookingListRequest(arg) {
  if (!(arg instanceof booking_pb.BookingListRequest)) {
    throw new Error('Expected argument of type booking.BookingListRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_booking_BookingListRequest(buffer_arg) {
  return booking_pb.BookingListRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_booking_BookingListResponse(arg) {
  if (!(arg instanceof booking_pb.BookingListResponse)) {
    throw new Error('Expected argument of type booking.BookingListResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_booking_BookingListResponse(buffer_arg) {
  return booking_pb.BookingListResponse.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_booking_BookingRequest(arg) {
  if (!(arg instanceof booking_pb.BookingRequest)) {
    throw new Error('Expected argument of type booking.BookingRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_booking_BookingRequest(buffer_arg) {
  return booking_pb.BookingRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_booking_BookingResponse(arg) {
  if (!(arg instanceof booking_pb.BookingResponse)) {
    throw new Error('Expected argument of type booking.BookingResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_booking_BookingResponse(buffer_arg) {
  return booking_pb.BookingResponse.deserializeBinary(new Uint8Array(buffer_arg));
}


// gRPC-сервис бронирования
var BookingServiceService = exports.BookingServiceService = {
  createBooking: {
    path: '/booking.BookingService/CreateBooking',
    requestStream: false,
    responseStream: false,
    requestType: booking_pb.BookingRequest,
    responseType: booking_pb.BookingResponse,
    requestSerialize: serialize_booking_BookingRequest,
    requestDeserialize: deserialize_booking_BookingRequest,
    responseSerialize: serialize_booking_BookingResponse,
    responseDeserialize: deserialize_booking_BookingResponse,
  },
  listBookings: {
    path: '/booking.BookingService/ListBookings',
    requestStream: false,
    responseStream: false,
    requestType: booking_pb.BookingListRequest,
    responseType: booking_pb.BookingListResponse,
    requestSerialize: serialize_booking_BookingListRequest,
    requestDeserialize: deserialize_booking_BookingListRequest,
    responseSerialize: serialize_booking_BookingListResponse,
    responseDeserialize: deserialize_booking_BookingListResponse,
  },
};

exports.BookingServiceClient = grpc.makeGenericClientConstructor(BookingServiceService, 'BookingService');
