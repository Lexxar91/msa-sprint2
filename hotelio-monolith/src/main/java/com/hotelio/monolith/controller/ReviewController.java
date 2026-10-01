package com.hotelio.monolith.controller;

import com.hotelio.monolith.entity.Review;
import com.hotelio.monolith.repository.ReviewRepository;
import com.hotelio.monolith.service.ReviewService;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST-контроллер ReviewController в системе Hotelio.
 */
@RestController
@RequestMapping("/api/reviews")
public class ReviewController {

    private final ReviewService reviewService;
    private final ReviewRepository reviewRepository;

    /**
     * Создаёт ReviewController с переданными зависимостями или данными.
     *
     * @param reviewService review service
     * @param reviewRepository review repository
     */
    public ReviewController(ReviewService reviewService, ReviewRepository reviewRepository) {
        this.reviewService = reviewService;
        this.reviewRepository = reviewRepository;
    }

    /**
     * Возвращает отзывы выбранного отеля.
     *
     * @param hotelId идентификатор отеля
     * @return результат операции
     */
    @GetMapping("/hotel/{hotelId}")
    public List<Review> getReviewsForHotel(@PathVariable String hotelId) {
        return reviewRepository.findByHotelId(hotelId);
    }

    /**
     * Проверяет пороги среднего рейтинга и количества отзывов.
     *
     * @param hotelId идентификатор отеля
     * @return результат проверки
     */
    @GetMapping("/hotel/{hotelId}/trusted")
    public boolean isHotelTrusted(@PathVariable String hotelId) {
        return reviewService.isTrustedHotel(hotelId);
    }
}
