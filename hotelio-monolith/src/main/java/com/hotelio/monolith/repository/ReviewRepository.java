package com.hotelio.monolith.repository;

import com.hotelio.monolith.entity.Review;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Репозиторий ReviewRepository в системе Hotelio.
 */
public interface ReviewRepository extends JpaRepository<Review, String> {
    /**
     * Ищет записи по критериям, указанным в имени метода.
     *
     * @param hotelId идентификатор отеля
     * @return результат операции
     */
    List<Review> findByHotelId(String hotelId);
    /**
     * Подсчитывает записи по заданному критерию.
     *
     * @param hotelId идентификатор отеля
     * @return результат операции
     */
    int countByHotelId(String hotelId);
}
