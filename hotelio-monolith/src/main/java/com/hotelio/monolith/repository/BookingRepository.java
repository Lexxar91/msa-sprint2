package com.hotelio.monolith.repository;

import com.hotelio.monolith.entity.Booking;
import java.util.List;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Репозиторий BookingRepository в системе Hotelio.
 */
public interface BookingRepository extends JpaRepository<Booking, Long> {
    /**
     * Ищет записи по критериям, указанным в имени метода.
     *
     * @param userId идентификатор пользователя
     * @return результат операции
     */
    List<Booking> findByUserId(String userId);
}
