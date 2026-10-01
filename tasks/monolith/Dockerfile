FROM eclipse-temurin:17-jre

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY hotelio-monolith-1.0.0.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
