package com.hotelio.monolith.repository;

import com.hotelio.monolith.entity.PromoCode;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Репозиторий PromoCodeRepository в системе Hotelio.
 */
public interface PromoCodeRepository extends JpaRepository<PromoCode, String> {}
