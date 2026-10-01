package com.hotelio.monolith;

import com.hotelio.monolith.service.BookingService;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;

/**
 * Приложение MonolithApplication в системе Hotelio.
 */
@SpringBootApplication(scanBasePackages = { "com.hotelio", "com.hotelio.monolith" })
public class MonolithApplication {

    /**
     * Запускает приложение Spring Boot.
     *
     * @param args args
     */
    public static void main(String[] args) {
        SpringApplication.run(MonolithApplication.class, args);
    }

    /**
     * Создаёт команду диагностики зарегистрированных сервисов.
     *
     * @param ctx ctx
     * @return результат операции
     */
    @Bean
    public CommandLineRunner logBeans(ApplicationContext ctx) {
        return args -> {
            String[] beans = ctx.getBeanNamesForType(BookingService.class);
            System.out.println("➡️  BookingService beans:");
            for (String name : beans) {
                System.out.println("    - " + name + ": " + ctx.getBean(name).getClass());
            }
        };
    }
}
