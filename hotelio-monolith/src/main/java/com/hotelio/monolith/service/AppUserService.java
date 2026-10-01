package com.hotelio.monolith.service;

import com.hotelio.monolith.entity.AppUser;
import com.hotelio.monolith.repository.AppUserRepository;
import java.util.Optional;
import org.springframework.stereotype.Service;

/**
 * Сервис AppUserService в системе Hotelio.
 */
@Service
public class AppUserService {

    private final AppUserRepository repository;

    /**
     * Создаёт AppUserService с переданными зависимостями или данными.
     *
     * @param repository repository
     */
    public AppUserService(AppUserRepository repository) {
        this.repository = repository;
    }

    /**
     * Возвращает user blacklisted.
     *
     * @param userId идентификатор пользователя
     * @return результат проверки
     */
    public boolean isUserBlacklisted(String userId) {
        return repository.findById(userId).map(AppUser::isBlacklisted).orElse(false);
    }

    /**
     * Возвращает user active.
     *
     * @param userId идентификатор пользователя
     * @return результат проверки
     */
    public boolean isUserActive(String userId) {
        return repository.findById(userId).map(AppUser::isActive).orElse(false);
    }

    /**
     * Возвращает user status.
     *
     * @param userId идентификатор пользователя
     * @return результат операции
     */
    public Optional<String> getUserStatus(String userId) {
        return repository.findById(userId).map(AppUser::getStatus);
    }

    /**
     * Возвращает user by id.
     *
     * @param userId идентификатор пользователя
     * @return результат операции
     */
    public Optional<AppUser> getUserById(String userId) {
        return repository.findById(userId);
    }

    /**
     * Проверяет VIP-статус пользователя.
     *
     * @param userId идентификатор пользователя
     * @return результат проверки
     */
    public boolean isVipUser(String userId) {
        return repository
            .findById(userId)
            .map(user -> "VIP".equalsIgnoreCase(user.getStatus()))
            .orElse(false);
    }

    /**
     * Проверяет активность пользователя и отсутствие блокировки.
     *
     * @param userId идентификатор пользователя
     * @return результат проверки
     */
    public boolean isAuthorized(String userId) {
        return repository
            .findById(userId)
            .map(user -> user.isActive() && !user.isBlacklisted())
            .orElse(false);
    }
}
