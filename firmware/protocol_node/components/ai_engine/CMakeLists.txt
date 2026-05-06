idf_component_register(SRCS "ai_model_manager.c"
                    "ai_inference.cpp"
                    "ai_ring_buffer.c"
                    "ai_data_collector.c"
                INCLUDE_DIRS "include"
                PRIV_INCLUDE_DIRS "../../main"
                REQUIRES esp_timer esp_partition esp-tflite-micro driver)
