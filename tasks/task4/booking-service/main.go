package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
)

// main запускает HTTP-сервис с проверкой доступности и флагом функции.
func main() {
	enableFeatureX := os.Getenv("ENABLE_FEATURE_X") == "true"
	http.HandleFunc("/ping",
		// Возвращает pong для проверки доступности; w — ответ, r — запрос.
		func(w http.ResponseWriter, r *http.Request) {
			fmt.Fprintf(w, "pong")
		})
	if enableFeatureX {
		http.HandleFunc("/feature",
			// Возвращает результат включённой функции; w — ответ, r — запрос.
			func(w http.ResponseWriter, r *http.Request) {
				fmt.Fprintf(w, "Feature X is enabled!")
			})
	}

	log.Println("Server running on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
