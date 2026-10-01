package com.hotelio.monolith.controller;

import com.hotelio.monolith.entity.Booking;
import com.hotelio.monolith.service.BookingService;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST-контроллер BookingController в системе Hotelio.
 */
@RestController
@RequestMapping("/api/bookings")
public class BookingController {

    private final BookingService bookingService;

    /**
     * Создаёт BookingController с переданными зависимостями или данными.
     *
     * @param bookingService booking service
     */
    public BookingController(BookingService bookingService) {
        this.bookingService = bookingService;
    }

    /**
     * Возвращает бронирования с необязательным фильтром по пользователю.
     *
     * @param userId идентификатор пользователя
     * @return результат операции
     */
    @GetMapping
    public List<Booking> listBookings(@RequestParam(required = false) String userId) {
        return bookingService.listAll(userId);
    }

    /**
     * Создаёт бронирование после проверки пользователя, отеля и промокода.
     *
     * @param userId идентификатор пользователя
     * @param hotelId идентификатор отеля
     * @param promoCode промокод
     * @return результат операции
     */
    @PostMapping
    public ResponseEntity<Booking> createBooking(
        @RequestParam String userId,
        @RequestParam String hotelId,
        @RequestParam(required = false) String promoCode
    ) {
        Booking booking = bookingService.createBooking(userId, hotelId, promoCode);
        return ResponseEntity.ok(booking);
    }
}
