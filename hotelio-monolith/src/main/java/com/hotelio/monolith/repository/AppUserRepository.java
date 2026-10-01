package com.hotelio.monolith.repository;

import com.hotelio.monolith.entity.AppUser;
import org.springframework.data.jpa.repository.JpaRepository;

/**
 * Репозиторий AppUserRepository в системе Hotelio.
 */
public interface AppUserRepository extends JpaRepository<AppUser, String> {}
