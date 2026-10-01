package com.hotelio.monolith.service;

import com.hotelio.monolith.entity.Hotel;
import com.hotelio.monolith.repository.HotelRepository;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;

/**
 * Сервис HotelService в системе Hotelio.
 */
@Service
public class HotelService {

    private final HotelRepository repo;

    /**
     * Создаёт HotelService с переданными зависимостями или данными.
     *
     * @param repo repo
     */
    public HotelService(HotelRepository repo) {
        this.repo = repo;
    }

    /**
     * Возвращает hotel operational.
     *
     * @param hotelId идентификатор отеля
     * @return результат проверки
     */
    public boolean isHotelOperational(String hotelId) {
        return repo.findById(hotelId).map(Hotel::isOperational).orElse(false);
    }

    /**
     * Возвращает hotel fully booked.
     *
     * @param hotelId идентификатор отеля
     * @return результат проверки
     */
    public boolean isHotelFullyBooked(String hotelId) {
        return repo.findById(hotelId).map(Hotel::isFullyBooked).orElse(true);
    }

    /**
     * Возвращает hotel by id.
     *
     * @param hotelId идентификатор отеля
     * @return результат операции
     */
    public Optional<Hotel> getHotelById(String hotelId) {
        return repo.findById(hotelId);
    }

    /**
     * Ищет записи по критериям, указанным в имени метода.
     *
     * @param city город
     * @return результат операции
     */
    public List<Hotel> findHotelsInCity(String city) {
        if (city == null || city.isBlank()) return Collections.emptyList();
        return repo.findByCity(city);
    }

    /**
     * Ищет записи по критериям, указанным в имени метода.
     *
     * @param city город
     * @param limit limit
     * @return результат операции
     */
    public List<Hotel> findTopRatedHotelsInCity(String city, int limit) {
        if (city == null || city.isBlank()) return Collections.emptyList();
        return repo.findByCityOrderByRatingDesc(city).stream().limit(limit).toList();
    }
}
