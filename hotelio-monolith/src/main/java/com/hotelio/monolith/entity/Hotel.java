package com.hotelio.monolith.entity;

import jakarta.persistence.*;

/**
 * Сущность Hotel в системе Hotelio.
 */
@Entity
public class Hotel {

    @Id
    private String id;

    private boolean operational;
    private boolean fullyBooked;

    private String city;
    private double rating;

    @Column(length = 1000)
    private String description;

    /**
     * Возвращает идентификатор записи.
     *
     * @return результат операции
     */
    public String getId() {
        return id;
    }

    /**
     * Возвращает признак работы отеля.
     *
     * @return результат проверки
     */
    public boolean isOperational() {
        return operational;
    }

    /**
     * Устанавливает признак работы отеля.
     *
     * @param operational признак работы отеля
     */
    public void setOperational(boolean operational) {
        this.operational = operational;
    }

    /**
     * Возвращает признак полной занятости отеля.
     *
     * @return результат проверки
     */
    public boolean isFullyBooked() {
        return fullyBooked;
    }

    /**
     * Устанавливает признак полной занятости отеля.
     *
     * @param fullyBooked признак полной занятости отеля
     */
    public void setFullyBooked(boolean fullyBooked) {
        this.fullyBooked = fullyBooked;
    }

    /**
     * Возвращает город.
     *
     * @return результат операции
     */
    public String getCity() {
        return city;
    }

    /**
     * Устанавливает город.
     *
     * @param city город
     */
    public void setCity(String city) {
        this.city = city;
    }

    /**
     * Возвращает рейтинг.
     *
     * @return результат операции
     */
    public double getRating() {
        return rating;
    }

    /**
     * Устанавливает рейтинг.
     *
     * @param rating рейтинг
     */
    public void setRating(double rating) {
        this.rating = rating;
    }

    /**
     * Возвращает описание.
     *
     * @return результат операции
     */
    public String getDescription() {
        return description;
    }

    /**
     * Устанавливает описание.
     *
     * @param description описание
     */
    public void setDescription(String description) {
        this.description = description;
    }
}
