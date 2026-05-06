#include "ai_ring_buffer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include <string.h>

static const char *TAG = "AI_RING_BUF";

typedef struct {
    float values[AI_FEATURE_DIM];
} feature_vector_t;

static QueueHandle_t s_queue = NULL;

esp_err_t ai_ring_buffer_init(void) {
    if (s_queue != NULL) return ESP_OK;

    // Use heap_caps_malloc to ensure the queue storage is in PSRAM if possible, 
    // although FreeRTOS queues are typically small and fit in SRAM.
    // Here we just use the standard xQueueCreate.
    s_queue = xQueueCreate(AI_RING_BUFFER_DEPTH, sizeof(feature_vector_t));
    if (s_queue == NULL) {
        ESP_LOGE(TAG, "Failed to create feature vector queue");
        return ESP_ERR_NO_MEM;
    }

    ESP_LOGI(TAG, "AI Ring Buffer initialized (Depth: %d)", AI_RING_BUFFER_DEPTH);
    return ESP_OK;
}

esp_err_t ai_ring_buffer_push(const float *features) {
    if (s_queue == NULL) return ESP_ERR_INVALID_STATE;

    feature_vector_t vector;
    memcpy(vector.values, features, sizeof(vector.values));

    if (xQueueSend(s_queue, &vector, 0) != pdTRUE) {
        // Buffer full - drop oldest and retry? 
        // For simplicity, we just return fail. The protocol task can decide what to do.
        return ESP_FAIL;
    }
    return ESP_OK;
}

esp_err_t ai_ring_buffer_pop(float *out_features, uint32_t wait_ms) {
    if (s_queue == NULL) return ESP_ERR_INVALID_STATE;

    feature_vector_t vector;
    if (xQueueReceive(s_queue, &vector, pdMS_TO_TICKS(wait_ms)) != pdTRUE) {
        return ESP_ERR_TIMEOUT;
    }

    memcpy(out_features, vector.values, sizeof(vector.values));
    return ESP_OK;
}
