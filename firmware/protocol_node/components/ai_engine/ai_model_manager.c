#include "ai_model_manager.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include <string.h>
#include "anomaly_detector.h" // Embedded model array

static const char *TAG = "EDGE_AI_MGR";

static const void *s_model_data = anomaly_detector_tflite;
static size_t s_model_size = sizeof(anomaly_detector_tflite);
static ai_metadata_t *s_meta_data = NULL;
static uint16_t s_model_crc = 0;

// Simple CRC16-CCITT implementation
static uint16_t calc_crc16(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int j = 0; j < 8; j++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

esp_err_t ai_model_manager_init(void) {
    ESP_LOGI(TAG, "Loading embedded AI model (%zu bytes)...", s_model_size);

    // Verify model
    s_model_crc = calc_crc16((const uint8_t *)s_model_data, s_model_size);
    ESP_LOGI(TAG, "Model verified. CRC16: 0x%04X", s_model_crc);

    // Initialize Metadata (Normalization parameters from training)
    if (s_meta_data == NULL) {
        s_meta_data = (ai_metadata_t *)heap_caps_malloc(sizeof(ai_metadata_t), MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
        if (s_meta_data) {
            // Use auto-generated normalization metadata from anomaly_detector.h
            for (int i = 0; i < AI_FEATURE_DIM; i++) {
                s_meta_data->norms[i].min_val = ANOMALY_MODEL_NORMS[i].min;
                s_meta_data->norms[i].max_val = ANOMALY_MODEL_NORMS[i].max;
            }
            ESP_LOGI(TAG, "Normalization metadata loaded from header.");
        } else {
            ESP_LOGE(TAG, "Metadata allocation failed");
            return ESP_ERR_NO_MEM;
        }
    }

    return ESP_OK;
}

const void* ai_model_manager_get_meta_ptr(void) {
    return s_meta_data;
}

const void* ai_model_manager_get_model_ptr(void) {
    return s_model_data;
}

size_t ai_model_manager_get_model_size(void) {
    return s_model_size;
}

uint16_t ai_model_manager_get_model_crc(void) {
    return s_model_crc;
}
