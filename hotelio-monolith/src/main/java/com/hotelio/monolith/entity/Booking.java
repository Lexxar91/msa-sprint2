package com.hotelio.monolith.entity;

import jakarta.persistence.*;
import java.time.Instant;

/**
 * Сущность Booking в системе Hotelio.
 */
@Entity
public class Booking {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String userId;
    private String hotelId;

    private String promoCode;
    private Double discountPercent;

    @Column(nullable = false)
    private Double price;

    private Instant createdAt;

    /**
     * Возвращает идентификатор записи.
     *
     * @return результат операции
     */
    public Long getId() {
        return id;
    }

    /**
     * Устанавливает идентификатор записи.
     *
     * @param id идентификатор записи
     */
    public void setId(Long id) {
        this.id = id;
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
     * Возвращает промокод.
     *
     * @return результат операции
     */
    public String getPromoCode() {
        return promoCode;
    }

    /**
     * Устанавливает промокод.
     *
     * @param promoCode промокод
     */
    public void setPromoCode(String promoCode) {
        this.promoCode = promoCode;
    }

    /**
     * Возвращает сохранённое значение скидки.
     *
     * @return результат операции
     */
    public Double getDiscountPercent() {
        return discountPercent;
    }

    /**
     * Устанавливает сохранённое значение скидки.
     *
     * @param discountPercent сохранённое значение скидки
     */
    public void setDiscountPercent(Double discountPercent) {
        this.discountPercent = discountPercent;
    }

    /**
     * Возвращает цену бронирования.
     *
     * @return результат операции
     */
    public Double getPrice() {
        return price;
    }

    /**
     * Устанавливает цену бронирования.
     *
     * @param price цену бронирования
     */
    public void setPrice(Double price) {
        this.price = price;
    }

    /**
     * Возвращает дату создания.
     *
     * @return результат операции
     */
    public Instant getCreatedAt() {
        return createdAt;
    }

    /**
     * Устанавливает дату создания.
     *
     * @param createdAt дату создания
     */
    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}
