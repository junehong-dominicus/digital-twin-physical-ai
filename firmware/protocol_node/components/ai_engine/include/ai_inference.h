#ifndef AI_INFERENCE_H
#define AI_INFERENCE_H

#include "esp_err.h"
#include <stdbool.h>
#include <stdint.h>

typedef enum {
    AI_MODE_IDLE = 0,
    AI_MODE_STATISTICAL = 1, // Simple Z-score logic (previously edge_ai)
    AI_MODE_ANOMALY = 2,     // MLP / TFLM path
    AI_MODE_PREDICTIVE = 3   // GRU / Sliding Window path
} ai_mode_t;

/**
 * @brief Unified AI Inference result.
 */
typedef struct {
    float    anomaly_score;    // 0.0 to 1.0
    bool     is_anomaly;       // Threshold-based flag
    char     reason[32];       // Descriptive reason
    uint32_t inference_time_ms;
    ai_mode_t mode;
} ai_result_t;

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize the inference engine and start the AI task
 * 
 * @return esp_err_t ESP_OK on success
 */
esp_err_t ai_inference_init(void);

/**
 * @brief Set the active inference mode
 * 
 * @param mode The desired mode
 * @return esp_err_t ESP_OK on success
 */
esp_err_t ai_inference_set_mode(ai_mode_t mode);

/**
 * @brief Get the current inference mode
 * 
 * @return ai_mode_t Current mode
 */
ai_mode_t ai_inference_get_mode(void);

/**
 * @brief Get the last calculated anomaly score and result details
 * 
 * @param out_result Pointer to store the last result
 * @return esp_err_t ESP_OK on success
 */
esp_err_t ai_inference_get_last_result(ai_result_t *out_result);

#ifdef __cplusplus
}
#endif

#endif // AI_INFERENCE_H

