#ifndef AI_MODEL_MANAGER_H
#define AI_MODEL_MANAGER_H

#include "esp_err.h"
#include "ai_config.h"
#include <stdint.h>
#include <stddef.h>

typedef struct {
    float min_val;
    float max_val;
} feature_norm_t;

typedef struct {
    feature_norm_t norms[AI_FEATURE_DIM];
} ai_metadata_t;

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Initialize the model manager and load the model from flash into PSRAM
 * 
 * @return esp_err_t ESP_OK on success
 */
esp_err_t ai_model_manager_init(void);

/**
 * @brief Get the pointer to the loaded model data in PSRAM
 * 
 * @return const void* Pointer to model data
 */
const void* ai_model_manager_get_model_ptr(void);

/**
 * @brief Get the size of the loaded model
 * 
 * @return size_t Model size in bytes
 */
size_t ai_model_manager_get_model_size(void);

/**
 * @brief Get the CRC16 of the loaded model
 * 
 * @return uint16_t CRC16 value
 */
uint16_t ai_model_manager_get_model_crc(void);

/**
 * @brief Get the pointer to the loaded metadata in PSRAM
 * 
 * @return const void* Pointer to metadata data
 */
const void* ai_model_manager_get_meta_ptr(void);

#ifdef __cplusplus
}
#endif

#endif // AI_MODEL_MANAGER_H
