package com.hotelio.monolith.repository;

import com.hotelio.monolith.entity.Hotel;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Репозиторий HotelRepository в системе Hotelio.
 */
public interface HotelRepository extends JpaRepository<Hotel, String> {
    /**
     * Ищет отели в выбранном городе.
     *
     * @param city город
     * @return результат операции
     */
    List<Hotel> findByCity(String city);

    /**
     * Ищет записи по критериям, указанным в имени метода.
     *
     * @param city город
     * @return результат операции
     */
    List<Hotel> findByCityOrderByRatingDesc(String city);
}
