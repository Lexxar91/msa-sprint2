package com.hotelio.monolith.entity;

import jakarta.persistence.*;

/**
 * Сущность AppUser в системе Hotelio.
 */
@Entity
@Table(name = "app_user")
public class AppUser {

    @Id
    private String id;

    private String status;
    private boolean blacklisted;
    private boolean active;

    private String name;
    private String email;
    private String city;

    /**
     * Создаёт AppUser с переданными зависимостями или данными.
     */
    public AppUser() {}

    /**
     * Создаёт AppUser с переданными зависимостями или данными.
     *
     * @param id идентификатор записи
     * @param status статус пользователя
     * @param blacklisted признак нахождения в чёрном списке
     * @param active признак активности
     */
    public AppUser(String id, String status, boolean blacklisted, boolean active) {
        this.id = id;
        this.status = status;
        this.blacklisted = blacklisted;
        this.active = active;
    }

    /**
     * Возвращает идентификатор записи.
     *
     * @return результат операции
     */
    public String getId() {
        return id;
    }

    /**
     * Устанавливает идентификатор записи.
     *
     * @param id идентификатор записи
     */
    public void setId(String id) {
        this.id = id;
    }

    /**
     * Возвращает статус пользователя.
     *
     * @return результат операции
     */
    public String getStatus() {
        return status;
    }

    /**
     * Устанавливает статус пользователя.
     *
     * @param status статус пользователя
     */
    public void setStatus(String status) {
        this.status = status;
    }

    /**
     * Возвращает признак нахождения в чёрном списке.
     *
     * @return результат проверки
     */
    public boolean isBlacklisted() {
        return blacklisted;
    }

    /**
     * Устанавливает признак нахождения в чёрном списке.
     *
     * @param blacklisted признак нахождения в чёрном списке
     */
    public void setBlacklisted(boolean blacklisted) {
        this.blacklisted = blacklisted;
    }

    /**
     * Возвращает признак активности.
     *
     * @return результат проверки
     */
    public boolean isActive() {
        return active;
    }

    /**
     * Устанавливает признак активности.
     *
     * @param active признак активности
     */
    public void setActive(boolean active) {
        this.active = active;
    }

    /**
     * Возвращает имя.
     *
     * @return результат операции
     */
    public String getName() {
        return name;
    }

    /**
     * Устанавливает имя.
     *
     * @param name имя
     */
    public void setName(String name) {
        this.name = name;
    }

    /**
     * Возвращает электронную почту.
     *
     * @return результат операции
     */
    public String getEmail() {
        return email;
    }

    /**
     * Устанавливает электронную почту.
     *
     * @param email электронную почту
     */
    public void setEmail(String email) {
        this.email = email;
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
}
