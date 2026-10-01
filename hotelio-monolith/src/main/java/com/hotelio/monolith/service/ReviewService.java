package com.hotelio.monolith.service;

import com.hotelio.monolith.entity.Review;
import com.hotelio.monolith.repository.ReviewRepository;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;

/**
 * Сервис ReviewService в системе Hotelio.
 */
@Service
public class ReviewService {

    private final ReviewRepository reviewRepository;

    /**
     * Создаёт ReviewService с переданными зависимостями или данными.
     *
     * @param reviewRepository review repository
     */
    public ReviewService(ReviewRepository reviewRepository) {
        this.reviewRepository = reviewRepository;
    }

    /**
     * Возвращает trusted hotel.
     *
     * @param hotelId идентификатор отеля
     * @return результат проверки
     */
    public boolean isTrustedHotel(String hotelId) {
        Optional<ReviewAggregate> aggregate = getAggregateForHotel(hotelId);
        return aggregate
            .map(agg -> agg.getAvgRating() >= 4.0 && agg.getReviewCount() >= 10)
            .orElse(false);
    }

    /**
     * Возвращает aggregate for hotel.
     *
     * @param hotelId идентификатор отеля
     * @return результат операции
     */
    private Optional<ReviewAggregate> getAggregateForHotel(String hotelId) {
        List<Review> reviews = reviewRepository.findByHotelId(hotelId);
        if (reviews.isEmpty()) return Optional.empty();

        double avg = reviews.stream().mapToInt(Review::getRating).average().orElse(0);
        return Optional.of(new ReviewAggregate(avg, reviews.size()));
    }

    /**
     * Сервис ReviewAggregate в системе Hotelio.
     */
    private static class ReviewAggregate {

        private final double avgRating;
        private final int reviewCount;

        /**
         * Создаёт ReviewAggregate с переданными зависимостями или данными.
         *
         * @param avgRating средний рейтинг
         * @param reviewCount количество отзывов
         */
        public ReviewAggregate(double avgRating, int reviewCount) {
            this.avgRating = avgRating;
            this.reviewCount = reviewCount;
        }

        /**
         * Возвращает средний рейтинг.
         *
         * @return результат операции
         */
        public double getAvgRating() {
            return avgRating;
        }

        /**
         * Возвращает количество отзывов.
         *
         * @return результат операции
         */
        public int getReviewCount() {
            return reviewCount;
        }
    }
}
