#include <stdio.h>
#include <string.h>
#include <math.h>
#include "ai_inference.h"
#include "ai_config.h"
#include "ai_model_manager.h"
#include "ai_ring_buffer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_heap_caps.h"
#include "driver/gpio.h"

// TFLM Includes
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/system_setup.h"
#include "tensorflow/lite/schema/schema_generated.h"

#ifdef CONFIG_DTPA_USE_EHIF_BRIDGE
#include "ehif_bridge.h"
#endif

static const char *TAG = "EDGE_AI";

static ai_mode_t s_mode = AI_MODE_STATISTICAL;
static uint8_t *s_tensor_arena = NULL;
static TaskHandle_t s_ai_task_handle = NULL;
static ai_result_t s_last_result = {0};

// TFLM Objects
static const tflite::Model* s_model = NULL;
static tflite::MicroInterpreter* s_interpreter = NULL;
static TfLiteTensor* s_input = NULL;
static TfLiteTensor* s_output = NULL;

// Statistical Mode Constants (Legacy Fallback)
static float s_mean_vibration = 0.02f;
static float s_std_vibration = 0.005f;

static void ai_inference_task(void *pvParameters) {
    float current_features[AI_FEATURE_DIM];
    float sliding_window[AI_WINDOW_SIZE][AI_FEATURE_DIM];
    int window_ptr = 0;
    int debounce_counter = 0;
    bool alarm_active = false;

    ESP_LOGI(TAG, "Edge AI Task started on Core %d", xPortGetCoreID());

    const ai_metadata_t *meta = (const ai_metadata_t *)ai_model_manager_get_meta_ptr();

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1)); // Safety yield

        // 1. Wait for data from sensor polling task
        if (ai_ring_buffer_pop(current_features, 100) != ESP_OK) {
            continue;
        }

        if (s_mode == AI_MODE_IDLE) {
            vTaskDelay(pdMS_TO_TICKS(100));
            continue;
        }

        uint32_t start_tick = xTaskGetTickCount();
        float score = 0.0f;
        char reason[32] = "Normal";

        // 2. Pre-process (Normalization for ML modes)
        float normalized_features[AI_FEATURE_DIM];
        memcpy(normalized_features, current_features, sizeof(normalized_features));

        if (s_mode == AI_MODE_ANOMALY || s_mode == AI_MODE_PREDICTIVE) {
            if (meta != NULL) {
                for (int i = 0; i < AI_FEATURE_DIM; i++) {
                    float min = meta->norms[i].min_val;
                    float max = meta->norms[i].max_val;
                    if (max > min) {
                        normalized_features[i] = (current_features[i] - min) / (max - min);
                        if (normalized_features[i] < 0.0f) normalized_features[i] = 0.0f;
                        if (normalized_features[i] > 1.0f) normalized_features[i] = 1.0f;
                    }
                }
            }
        }

        // 3. Inference
        if (s_mode == AI_MODE_STATISTICAL) {
            // Replicate old edge_ai logic
            float temp = current_features[0]; // Assuming temp is feature 0 in simple mode
            float vib = current_features[1];  // Assuming vib is feature 1 in simple mode
            float z_score = fabsf(vib - s_mean_vibration) / s_std_vibration;
            score = z_score / 10.0f;
            if (score > 1.0f) score = 1.0f;

            if (z_score > 3.0f) {
                strcpy(reason, "Abnormal Vibration");
            } else if (temp > 80.0f) {
                score = 0.9f;
                strcpy(reason, "Critical Heat");
            }
        } 
        else if (s_interpreter != NULL) {
            // MLP path
            if (s_mode == AI_MODE_ANOMALY) {
                for (int i = 0; i < AI_FEATURE_DIM; i++) {
                    s_input->data.f[i] = normalized_features[i];
                }
                if (s_interpreter->Invoke() == kTfLiteOk) {
                    score = s_output->data.f[0];
                    strcpy(reason, score > AI_ALARM_THRESHOLD ? "ML Anomaly" : "Normal");
                }
            } 
            // GRU path
            else if (s_mode == AI_MODE_PREDICTIVE) {
                memcpy(sliding_window[window_ptr], normalized_features, sizeof(normalized_features));
                window_ptr = (window_ptr + 1) % AI_WINDOW_SIZE;

                for (int w = 0; w < AI_WINDOW_SIZE; w++) {
                    int idx = (window_ptr + w) % AI_WINDOW_SIZE;
                    for (int n = 0; n < AI_FEATURE_DIM; n++) {
                        s_input->data.f[w * AI_FEATURE_DIM + n] = sliding_window[idx][n];
                    }
                }

                if (s_interpreter->Invoke() == kTfLiteOk) {
                    if (s_output->dims->size == 2 && s_output->dims->data[1] == AI_FEATURE_DIM) {
                        float mse = 0;
                        for (int i = 0; i < AI_FEATURE_DIM; i++) {
                            float diff = normalized_features[i] - s_output->data.f[i];
                            mse += diff * diff;
                        }
                        score = mse / AI_FEATURE_DIM;
                    } else {
                        score = s_output->data.f[0];
                    }
                    strcpy(reason, score > AI_ALARM_THRESHOLD ? "Predictive Alert" : "Normal");
                }
            }
        }

        // Update Last Result
        s_last_result.anomaly_score = score;
        s_last_result.is_anomaly = (score >= AI_ALARM_THRESHOLD);
        s_last_result.inference_time_ms = (xTaskGetTickCount() - start_tick) * portTICK_PERIOD_MS;
        s_last_result.mode = s_mode;
        strcpy(s_last_result.reason, reason);

        // 4. Alert & Debounce Logic
        if (s_last_result.is_anomaly) {
            debounce_counter++;
            if (debounce_counter >= AI_DEBOUNCE_CYCLES) {
                if (!alarm_active) {
                    ESP_LOGW(TAG, "ALERT! Score: %.2f, Reason: %s", score, reason);
                    alarm_active = true;
                    
#ifdef CONFIG_DTPA_USE_EHIF_BRIDGE
                    ehif_ai_alert_t alert = {
                        .alert_level = 2,
                        .anomaly_score = score,
                        .timestamp_ms = xTaskGetTickCount() * portTICK_PERIOD_MS,
                        .inference_mode = (uint8_t)s_mode
                    };
                    ehif_send(EHIF_CMD_AI_ALERT, 0, (uint8_t*)&alert, sizeof(alert));
#endif
                }
            }
        } else if (score < AI_WARN_THRESHOLD) {
            if (debounce_counter > 0) debounce_counter--;
            if (debounce_counter == 0 && alarm_active) {
                ESP_LOGI(TAG, "System Recovered to Normal.");
                alarm_active = false;
                
#ifdef CONFIG_DTPA_USE_EHIF_BRIDGE
                ehif_ai_alert_t alert = {
                    .alert_level = 0,
                    .anomaly_score = score,
                    .timestamp_ms = xTaskGetTickCount() * portTICK_PERIOD_MS,
                    .inference_mode = (uint8_t)s_mode
                };
                ehif_send(EHIF_CMD_AI_ALERT, 0, (uint8_t*)&alert, sizeof(alert));
#endif
            }
        }

        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

esp_err_t ai_inference_init(void) {
    if (ai_model_manager_init() != ESP_OK) {
        ESP_LOGE(TAG, "Model initialization failed. AI Engine disabled.");
        return ESP_FAIL;
    }

    if (ai_ring_buffer_init() != ESP_OK) {
        ESP_LOGE(TAG, "Ring buffer initialization failed.");
        return ESP_FAIL;
    }

    s_model = tflite::GetModel(ai_model_manager_get_model_ptr());
    if (s_model->version() != TFLITE_SCHEMA_VERSION) {
        ESP_LOGW(TAG, "Model schema mismatch. Waiting for OTA. Falling back to STATISTICAL mode.");
        s_mode = AI_MODE_STATISTICAL;
    } else {
        if (s_tensor_arena == NULL) {
            s_tensor_arena = (uint8_t*)heap_caps_malloc(AI_TFLM_ARENA_SIZE, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
            if (s_tensor_arena == NULL) {
                ESP_LOGE(TAG, "Arena allocation failed");
                return ESP_ERR_NO_MEM;
            }
        }

        static tflite::MicroMutableOpResolver<12> resolver;
        resolver.AddFullyConnected();
        resolver.AddRelu();
        resolver.AddSoftmax();
        resolver.AddReshape();
        resolver.AddTanh();
        resolver.AddLogistic();
        resolver.AddAdd();
        resolver.AddMul();

        static tflite::MicroInterpreter static_interpreter(s_model, resolver, s_tensor_arena, AI_TFLM_ARENA_SIZE);
        s_interpreter = &static_interpreter;

        if (s_interpreter->AllocateTensors() != kTfLiteOk) {
            ESP_LOGE(TAG, "AllocateTensors failed");
            s_mode = AI_MODE_STATISTICAL;
        } else {
            s_input = s_interpreter->input(0);
            s_output = s_interpreter->output(0);
            ESP_LOGI(TAG, "TFLM Interpreter ready.");
        }
    }

    if (s_ai_task_handle == NULL) {
        xTaskCreatePinnedToCore(ai_inference_task, "ai_task", AI_TASK_STACK_SIZE, NULL, 5, &s_ai_task_handle, 1);
    }

    ESP_LOGI(TAG, "Edge AI Engine initialized. Mode: %d", (int)s_mode);
    return ESP_OK;
}

esp_err_t ai_inference_set_mode(ai_mode_t mode) {
    s_mode = mode;
    ESP_LOGI(TAG, "Mode set to %d", mode);
    return ESP_OK;
}

ai_mode_t ai_inference_get_mode(void) {
    return s_mode;
}

esp_err_t ai_inference_get_last_result(ai_result_t *out_result) {
    if (out_result == NULL) return ESP_ERR_INVALID_ARG;
    memcpy(out_result, &s_last_result, sizeof(ai_result_t));
    return ESP_OK;
}

