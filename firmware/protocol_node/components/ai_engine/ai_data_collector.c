#include "ai_data_collector.h"
#include "ai_config.h"
#include "ai_ring_buffer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"
#include <string.h>

static float s_current_features[AI_FEATURE_DIM] = {0};
static SemaphoreHandle_t s_mutex = NULL;

void ai_data_collector_set_feature(int index, float value) {
    if (index < 0 || index >= AI_FEATURE_DIM) return;

    if (s_mutex == NULL) {
        s_mutex = xSemaphoreCreateMutex();
    }

    xSemaphoreTake(s_mutex, portMAX_DELAY);
    s_current_features[index] = value;
    xSemaphoreGive(s_mutex);
}

void ai_data_collector_push_to_engine(void) {
    if (s_mutex == NULL) return;

    float vector_to_push[AI_FEATURE_DIM];
    
    xSemaphoreTake(s_mutex, portMAX_DELAY);
    memcpy(vector_to_push, s_current_features, sizeof(vector_to_push));
    xSemaphoreGive(s_mutex);

    ai_ring_buffer_push(vector_to_push);
}
