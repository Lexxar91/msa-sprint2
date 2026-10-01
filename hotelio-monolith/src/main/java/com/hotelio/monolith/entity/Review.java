package com.hotelio.monolith.entity;

import jakarta.persistence.*;
import java.time.LocalDate;

/**
 * Сущность Review в системе Hotelio.
 */
@Entity
public class Review {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    private String hotelId;
    private String userId;

    @Column(length = 2000)
    private String text;

    private int rating; // от 1 до 5
    private LocalDate createdAt;

    /**
     * Возвращает идентификатор записи.
     *
     * @return результат операции
     */
    public String getId() {
        return id;
    }

    /**
     * Возвращает идентификатор отеля.
     *
     * @return результат операции
     */
    public String getHotelId() {
        return hotelId;
    }

    /**
     * Устанавливает идентификатор отеля.
     *
     * @param hotelId идентификатор отеля
     */
    public void setHotelId(String hotelId) {
        this.hotelId = hotelId;
    }

    /**
     * Возвращает идентификатор пользователя.
     *
     * @return результат операции
     */
    public String getUserId() {
        return userId;
    }

    /**
     * Устанавливает идентификатор пользователя.
     *
     * @param userId идентификатор пользователя
     */
    public void setUserId(String userId) {
        this.userId = userId;
    }

    /**
     * Возвращает текст отзыва.
     *
     * @return результат операции
     */
    public String getText() {
        return text;
    }

    /**
     * Устанавливает текст отзыва.
     *
     * @param text текст отзыва
     */
    public void setText(String text) {
        this.text = text;
    }

    /**
     * Возвращает рейтинг.
     *
     * @return результат операции
     */
    public int getRating() {
        return rating;
    }

    /**
     * Устанавливает рейтинг.
     *
     * @param rating рейтинг
     */
    public void setRating(int rating) {
        this.rating = rating;
    }

    /**
     * Возвращает дату создания.
     *
     * @return результат операции
     */
    public LocalDate getCreatedAt() {
        return createdAt;
    }

    /**
     * Устанавливает дату создания.
     *
     * @param createdAt дату создания
     */
    public void setCreatedAt(LocalDate createdAt) {
        this.createdAt = createdAt;
    }
}
