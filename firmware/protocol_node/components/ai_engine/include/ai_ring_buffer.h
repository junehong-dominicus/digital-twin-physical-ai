#ifndef AI_RING_BUFFER_H
#define AI_RING_BUFFER_H

#include "esp_err.h"
#include "ai_config.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize the PSRAM ring buffer
 * 
 * @return esp_err_t ESP_OK on success
 */
esp_err_t ai_ring_buffer_init(void);

/**
 * @brief Push a new feature vector into the ring buffer (Thread-safe)
 * 
 * @param features Pointer to array of AI_FEATURE_DIM floats
 * @return esp_err_t ESP_OK on success, ESP_FAIL if buffer full
 */
esp_err_t ai_ring_buffer_push(const float *features);

/**
 * @brief Pop the oldest feature vector from the ring buffer (Thread-safe)
 * 
 * @param out_features Pointer to array of AI_FEATURE_DIM floats to store result
 * @param wait_ms Time to wait if buffer is empty
 * @return esp_err_t ESP_OK on success, ESP_ERR_TIMEOUT on timeout
 */
esp_err_t ai_ring_buffer_pop(float *out_features, uint32_t wait_ms);

#ifdef __cplusplus
}
#endif

#endif // AI_RING_BUFFER_H
