package com.hotelio.monolith.controller;

import com.hotelio.monolith.entity.Hotel;
import com.hotelio.monolith.service.HotelService;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST-контроллер HotelController в системе Hotelio.
 */
@RestController
@RequestMapping("/api/hotels")
public class HotelController {

    private final HotelService hotelService;

    /**
     * Создаёт HotelController с переданными зависимостями или данными.
     *
     * @param hotelService hotel service
     */
    public HotelController(HotelService hotelService) {
        this.hotelService = hotelService;
    }

    /**
     * Возвращает hotel by id.
     *
     * @param id идентификатор записи
     * @return результат операции
     */
    @GetMapping("/{id}")
    public ResponseEntity<Hotel> getHotelById(@PathVariable String id) {
        return hotelService
            .getHotelById(id)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Возвращает признак работы отеля.
     *
     * @param id идентификатор записи
     * @return результат проверки
     */
    @GetMapping("/{id}/operational")
    public boolean isOperational(@PathVariable String id) {
        return hotelService.isHotelOperational(id);
    }

    /**
     * Возвращает признак полной занятости отеля.
     *
     * @param id идентификатор записи
     * @return результат проверки
     */
    @GetMapping("/{id}/fully-booked")
    public boolean isFullyBooked(@PathVariable String id) {
        return hotelService.isHotelFullyBooked(id);
    }

    /**
     * Ищет отели в выбранном городе.
     *
     * @param city город
     * @return результат операции
     */
    @GetMapping("/by-city")
    public List<Hotel> findByCity(@RequestParam String city) {
        return hotelService.findHotelsInCity(city);
    }

    /**
     * Выполняет операцию topRatedInCity.
     *
     * @param city город
     * @param limit limit
     * @return результат операции
     */
    @GetMapping("/top-rated")
    public List<Hotel> topRatedInCity(
        @RequestParam String city,
        @RequestParam(defaultValue = "5") int limit
    ) {
        return hotelService.findTopRatedHotelsInCity(city, limit);
    }
}
