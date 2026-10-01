package com.hotelio.monolith.service;

import com.hotelio.monolith.entity.PromoCode;
import com.hotelio.monolith.repository.PromoCodeRepository;
import java.util.Optional;
import org.springframework.stereotype.Service;

/**
 * Сервис PromoCodeService в системе Hotelio.
 */
@Service
public class PromoCodeService {

    private final PromoCodeRepository repository;
    private final AppUserService userService;

    /**
     * Создаёт PromoCodeService с переданными зависимостями или данными.
     *
     * @param repository repository
     * @param userService user service
     */
    public PromoCodeService(PromoCodeRepository repository, AppUserService userService) {
        this.repository = repository;
        this.userService = userService;
    }

    /**
     * Проверяет срок действия промокода и требование VIP-статуса.
     *
     * @param code код промокода
     * @param isVipUser is vip user
     * @return результат операции
     */
    public Optional<PromoCode> getValidPromo(String code, boolean isVipUser) {
        return repository
            .findById(code)
            .filter(p -> !p.isExpired())
            .filter(p -> !p.isVipOnly() || isVipUser);
    }

    /**
     * Ищет записи по критериям, указанным в имени метода.
     *
     * @param code код промокода
     * @return результат операции
     */
    public Optional<PromoCode> findByCode(String code) {
        return repository.findById(code);
    }

    /**
     * Выполняет операцию validate.
     *
     * @param promoCode промокод
     * @param userId идентификатор пользователя
     * @return результат операции
     */
    public PromoCode validate(String promoCode, String userId) {
        Optional<String> status = userService.getUserStatus(userId);
        boolean isVip = status.map("VIP"::equalsIgnoreCase).orElse(false);
        return getValidPromo(promoCode, isVip).orElse(null);
    }

    /**
     * Проверяет допустимость промокода.
     *
     * @param code код промокода
     * @param isVipUser is vip user
     * @return результат проверки
     */
    public boolean isPromoValid(String code, boolean isVipUser) {
        return getValidPromo(code, isVipUser).isPresent();
    }
}
