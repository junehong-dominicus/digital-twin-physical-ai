#ifndef AI_CONFIG_H
#define AI_CONFIG_H

#include "driver/gpio.h"

// Feature Vector Configuration
#define AI_FEATURE_DIM          6
#define AI_WINDOW_SIZE          10      // For GRU sliding window
#define AI_RING_BUFFER_DEPTH    128

// Thresholds & Debouncing
#define AI_WARN_THRESHOLD       0.65f
#define AI_ALARM_THRESHOLD      0.85f
#define AI_DEBOUNCE_CYCLES      3

// Timing
#define AI_INFERENCE_INTERVAL_MS 500
#define AI_WDT_TIMEOUT_MS        2000

// Hardware
// #define AI_ALARM_GPIO           GPIO_NUM_25

// Memory
#define AI_TASK_STACK_SIZE      (10 * 1024)
#define AI_TFLM_ARENA_SIZE      (64 * 1024)

#endif // AI_CONFIG_H
