#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_one.h"
#include "edge_ai.h"

static const char *TAG = "PROTOCOL_NODE";

// Simulated sensor reading logic
void poll_industrial_devices() {
    // 1. Poll raw data (Placeholder)
    float temperature = 25.5 + (rand() % 10);
    float vibration = 0.02 + ((float)(rand() % 100) / 1000.0f); // 0.02 to 0.12
    
    float sensors[2] = {temperature, vibration};

    // 2. Run Edgie AI Inference
    edge_ai_result_t ai_result;
    edge_ai_run_inference(sensors, 2, &ai_result);

    // 3. Normal Telemetry Flow
    uint8_t payload[16];
    memcpy(payload, &temperature, sizeof(float));
    esp_one_send(ESP_ONE_MSG_TELEMETRY, payload, sizeof(float));

    // 4. Edge AI Feedback Loop (Local Alerting)
    if (ai_result.is_anomaly) {
        ESP_LOGE(TAG, "!! ANOMALY DETECTED by Edgie AI: %s (Score: %.2f) !!", 
                 ai_result.reason, ai_result.anomaly_score);
        
        // Send high-priority alert to Gateway
        esp_one_send(ESP_ONE_MSG_ALERT, (uint8_t*)ai_result.reason, strlen(ai_result.reason));
    }
}

void app_main(void) {
    ESP_LOGI(TAG, "Initializing Protocol Node...");

    // 1. Initialize ESP-ONE (UART between nodes)
    esp_one_init(17, 16, 115200);

    // 2. Initialize Industrial Protocols (Modbus Master)
    // industrial_protocols_init();

    // 3. Initialize Edge AI Engine
    // edge_ai_init();

    while (1) {
        poll_industrial_devices();
        vTaskDelay(pdMS_TO_TICKS(5000)); // Poll every 5 seconds
    }
}
