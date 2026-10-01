package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
)

// main запускает HTTP-сервис с проверкой доступности и флагом функции.
func main() {
	version := os.Getenv("SERVICE_VERSION")
	if version == "" {
		version = "v1"
	}
	enableFeatureX := os.Getenv("ENABLE_FEATURE_X") == "true"

	handler := http.HandlerFunc(
		// Обрабатывает HTTP-запрос и формирует ответ текущей версии сервиса.
		func(w http.ResponseWriter, r *http.Request) {
			featureEnabled := version == "v2" && enableFeatureX && r.Header.Get("X-Feature-Enabled") == "true"
			w.Header().Set("X-Service-Version", version)
			w.Header().Set("X-Feature-Enabled", fmt.Sprint(featureEnabled))
			switch r.URL.Path {
			case "/ping":
				if version == "v1" && r.Header.Get("X-Demo-Failure") == "true" {
					log.Println("v1: simulated HTTP 503")
					http.Error(w, "v1: simulated failure", http.StatusServiceUnavailable)
					return
				}
				fmt.Fprintf(w, "pong %s", version)
			case "/feature":
				if !featureEnabled {
					http.NotFound(w, r)
					return
				}
				fmt.Fprint(w, "Feature X is enabled!")
			default:
				http.NotFound(w, r)
			}
		})
	log.Printf("Server %s running on :8080", version)
	log.Fatal(http.ListenAndServe(":8080", handler))
}
