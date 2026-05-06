#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_one.h"
#include "ai_inference.h"
#include "ai_ring_buffer.h"
#include "ai_config.h"

static const char *TAG = "PROTOCOL_NODE";

// Simulated sensor reading logic
void poll_industrial_devices() {
    // 1. Poll raw data (Simulating 6 dimensions for the AI Engine)
    float sensors[AI_FEATURE_DIM];
    sensors[0] = 25.5 + (rand() % 10);                     // Temperature
    sensors[1] = 0.02 + ((float)(rand() % 100) / 1000.0f); // Vibration
    sensors[2] = 10.0 + (rand() % 20);                     // Pressure
    sensors[3] = 24.0 + (rand() % 2);                      // Voltage
    sensors[4] = 0.0 + ((float)(rand() % 50) / 10.0f);     // Flow
    sensors[5] = 0.1 + ((float)(rand() % 10) / 100.0f);    // Heat Rate
    
    // 2. Push to AI Ring Buffer for asynchronous processing
    ai_ring_buffer_push(sensors);

    // 3. Fetch last inference result for local alerting
    ai_result_t ai_result;
    if (ai_inference_get_last_result(&ai_result) == ESP_OK) {
        if (ai_result.is_anomaly) {
            ESP_LOGE(TAG, "!! LOCAL ALERT: %s (Score: %.2f) !!", 
                     ai_result.reason, ai_result.anomaly_score);
            
            // Send high-priority alert to Gateway
            esp_one_send(ESP_ONE_MSG_ALERT, (uint8_t*)ai_result.reason, strlen(ai_result.reason));
        }
    }

    // 4. Normal Telemetry Flow (Send Temperature as example)
    esp_one_send(ESP_ONE_MSG_TELEMETRY, (uint8_t*)&sensors[0], sizeof(float));
}

void app_main(void) {
    ESP_LOGI(TAG, "Initializing Industrial Protocol Node...");

    // 1. Initialize ESP-ONE (UART communication)
    esp_one_init(17, 16, 115200);

    // 2. Initialize Edge AI Engine (TFLM + Statistical Fallback)
    if (ai_inference_init() == ESP_OK) {
        ESP_LOGI(TAG, "Edge AI Engine started successfully.");
    } else {
        ESP_LOGE(TAG, "Failed to start AI Engine.");
    }

    while (1) {
        poll_industrial_devices();
        vTaskDelay(pdMS_TO_TICKS(AI_INFERENCE_INTERVAL_MS)); // Follow config timing
    }
}

