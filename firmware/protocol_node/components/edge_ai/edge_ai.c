#include "edge_ai.h"
#include <string.h>
#include <math.h>
#include "esp_log.h"

static const char *TAG = "EDGIE_AI";

// Simple statistical model for simulation
// In production, this would be replaced by TFLite / ESP-DL model weights
static float mean_vibration = 0.02f;
static float std_vibration = 0.005f;
static float anomaly_threshold = 3.0f; // 3-sigma

void edge_ai_init(void) {
    ESP_LOGI(TAG, "Edgie AI Initialized. Loading statistical model...");
}

void edge_ai_run_inference(const float *input_data, size_t len, edge_ai_result_t *result) {
    // Assume input_data[0] is temperature, input_data[1] is vibration
    float temp = input_data[0];
    float vib = input_data[1];

    // Calculate Z-score for vibration (mock inference)
    float z_score = fabsf(vib - mean_vibration) / std_vibration;
    
    result->anomaly_score = z_score / 10.0f; // Normalized score
    if (result->anomaly_score > 1.0f) result->anomaly_score = 1.0f;

    if (z_score > anomaly_threshold || temp > 80.0f) {
        result->is_anomaly = true;
        if (temp > 80.0f) {
            strcpy(result->reason, "Critical Overheating");
        } else {
            strcpy(result->reason, "Abnormal Vibration");
        }
    } else {
        result->is_anomaly = false;
        strcpy(result->reason, "Normal");
    }

    result->inference_time_ms = 5; // Simulated 5ms inference
}
