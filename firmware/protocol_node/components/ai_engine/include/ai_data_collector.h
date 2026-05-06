#ifndef AI_DATA_COLLECTOR_H
#define AI_DATA_COLLECTOR_H

#include "esp_err.h"

/**
 * @brief Update a specific feature in the global feature vector
 * 
 * @param index Index of the feature (0 to AI_FEATURE_DIM-1)
 * @param value Raw float value
 */
void ai_data_collector_set_feature(int index, float value);

/**
 * @brief Push the current global feature vector to the inference ring buffer
 * This should be called at a regular interval (e.g., from a timer or one of the tasks)
 */
void ai_data_collector_push_to_engine(void);

#endif // AI_DATA_COLLECTOR_H
