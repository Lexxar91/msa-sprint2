package com.hotelio.monolith.controller;

import com.hotelio.monolith.entity.AppUser;
import com.hotelio.monolith.service.AppUserService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST-контроллер AppUserController в системе Hotelio.
 */
@RestController
@RequestMapping("/api/users")
public class AppUserController {

    private final AppUserService userService;

    /**
     * Создаёт AppUserController с переданными зависимостями или данными.
     *
     * @param userService user service
     */
    public AppUserController(AppUserService userService) {
        this.userService = userService;
    }

    /**
     * Возвращает user by id.
     *
     * @param userId идентификатор пользователя
     * @return результат операции
     */
    @GetMapping("/{userId}")
    public ResponseEntity<AppUser> getUserById(@PathVariable String userId) {
        return userService
            .getUserById(userId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Возвращает user status.
     *
     * @param userId идентификатор пользователя
     * @return результат операции
     */
    @GetMapping("/{userId}/status")
    public ResponseEntity<String> getUserStatus(@PathVariable String userId) {
        return ResponseEntity.of(userService.getUserStatus(userId));
    }

    /**
     * Возвращает user blacklisted.
     *
     * @param userId идентификатор пользователя
     * @return результат проверки
     */
    @GetMapping("/{userId}/blacklisted")
    public boolean isUserBlacklisted(@PathVariable String userId) {
        return userService.isUserBlacklisted(userId);
    }

    /**
     * Возвращает user active.
     *
     * @param userId идентификатор пользователя
     * @return результат проверки
     */
    @GetMapping("/{userId}/active")
    public boolean isUserActive(@PathVariable String userId) {
        return userService.isUserActive(userId);
    }

    /**
     * Возвращает user authorized.
     *
     * @param userId идентификатор пользователя
     * @return результат проверки
     */
    @GetMapping("/{userId}/authorized")
    public boolean isUserAuthorized(@PathVariable String userId) {
        return userService.isAuthorized(userId);
    }

    /**
     * Возвращает user vip.
     *
     * @param userId идентификатор пользователя
     * @return результат проверки
     */
    @GetMapping("/{userId}/vip")
    public boolean isUserVip(@PathVariable String userId) {
        return userService.isVipUser(userId);
    }
}
