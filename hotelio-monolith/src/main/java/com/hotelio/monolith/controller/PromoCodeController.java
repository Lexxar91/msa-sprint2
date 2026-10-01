package com.hotelio.monolith.controller;

import com.hotelio.monolith.entity.PromoCode;
import com.hotelio.monolith.service.PromoCodeService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST-контроллер PromoCodeController в системе Hotelio.
 */
@RestController
@RequestMapping("/api/promos")
public class PromoCodeController {

    private final PromoCodeService promoCodeService;

    /**
     * Создаёт PromoCodeController с переданными зависимостями или данными.
     *
     * @param promoCodeService promo code service
     */
    public PromoCodeController(PromoCodeService promoCodeService) {
        this.promoCodeService = promoCodeService;
    }

    /**
     * Возвращает promo by code.
     *
     * @param code код промокода
     * @return результат операции
     */
    @GetMapping("/{code}")
    public ResponseEntity<PromoCode> getPromoByCode(@PathVariable String code) {
        return promoCodeService
            .findByCode(code)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    /**
     * Проверяет допустимость промокода.
     *
     * @param code код промокода
     * @param isVipUser is vip user
     * @return результат проверки
     */
    @GetMapping("/{code}/valid")
    public boolean isPromoValid(
        @PathVariable String code,
        @RequestParam(defaultValue = "false") boolean isVipUser
    ) {
        return promoCodeService.isPromoValid(code, isVipUser);
    }

    /**
     * Возвращает промокод, допустимый для выбранного пользователя.
     *
     * @param code код промокода
     * @param userId идентификатор пользователя
     * @return результат операции
     */
    @PostMapping("/validate")
    public ResponseEntity<PromoCode> validatePromo(
        @RequestParam String code,
        @RequestParam String userId
    ) {
        PromoCode promo = promoCodeService.validate(code, userId);
        if (promo != null) {
            return ResponseEntity.ok(promo);
        } else {
            return ResponseEntity.badRequest().build();
        }
    }
}
