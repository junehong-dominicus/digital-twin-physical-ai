#ifndef EDGE_AI_H
#define EDGE_AI_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @brief Edge AI (Edgie AI) Inference result.
 */
typedef struct {
    float    anomaly_score; // 0.0 (Healthy) to 1.0 (Critical Anomaly)
    bool     is_anomaly;    // Threshold-based flag
    char     reason[32];    // Descriptive reason for the alert
    uint32_t inference_time_ms;
} edge_ai_result_t;

/**
 * @brief Initialize the Edge AI engine (load models, etc.).
 */
void edge_ai_init(void);

/**
 * @brief Run inference on a set of normalized sensor values.
 * 
 * @param input_data Array of floats (e.g., [temp, vib, rpm])
 * @param len Number of inputs
 * @param result Pointer to store inference result
 */
void edge_ai_run_inference(const float *input_data, size_t len, edge_ai_result_t *result);

#endif // EDGE_AI_H
