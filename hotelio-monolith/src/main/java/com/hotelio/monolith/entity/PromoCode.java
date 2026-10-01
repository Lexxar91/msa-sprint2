package com.hotelio.monolith.entity;

import jakarta.persistence.*;
import java.time.LocalDate;

/**
 * Сущность PromoCode в системе Hotelio.
 */
@Entity
public class PromoCode {

    @Id
    private String code;

    private double discount;
    private boolean vipOnly;
    private boolean expired;

    private LocalDate validUntil;
    private String description;

    /**
     * Возвращает код промокода.
     *
     * @return результат операции
     */
    public String getCode() {
        return code;
    }

    /**
     * Устанавливает код промокода.
     *
     * @param code код промокода
     */
    public void setCode(String code) {
        this.code = code;
    }

    /**
     * Возвращает значение скидки.
     *
     * @return результат операции
     */
    public double getDiscount() {
        return discount;
    }

    /**
     * Устанавливает значение скидки.
     *
     * @param discount значение скидки
     */
    public void setDiscount(double discount) {
        this.discount = discount;
    }

    /**
     * Возвращает ограничение для VIP-пользователей.
     *
     * @return результат проверки
     */
    public boolean isVipOnly() {
        return vipOnly;
    }

    /**
     * Устанавливает ограничение для VIP-пользователей.
     *
     * @param vipOnly ограничение для VIP-пользователей
     */
    public void setVipOnly(boolean vipOnly) {
        this.vipOnly = vipOnly;
    }

    /**
     * Возвращает признак истечения срока действия.
     *
     * @return результат проверки
     */
    public boolean isExpired() {
        return expired;
    }

    /**
     * Устанавливает признак истечения срока действия.
     *
     * @param expired признак истечения срока действия
     */
    public void setExpired(boolean expired) {
        this.expired = expired;
    }

    /**
     * Возвращает дату окончания действия.
     *
     * @return результат операции
     */
    public LocalDate getValidUntil() {
        return validUntil;
    }

    /**
     * Устанавливает дату окончания действия.
     *
     * @param validUntil дату окончания действия
     */
    public void setValidUntil(LocalDate validUntil) {
        this.validUntil = validUntil;
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
