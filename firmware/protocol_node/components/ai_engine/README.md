# AI Engine Component

This component implements the Edge AI inference engine for the Digital Twin Physical AI platform.

## Features
- **Real-time Inference**: Runs on ESP32-S3 Core 1.
- **TFLite Micro Integration**: Supports MLP and GRU models.
- **Multi-mode Operation**: Statistical, Anomaly (MLP), and Predictive (GRU).
- **Thread-safe Data Collection**: Decoupled from sensor tasks via ring buffers.

## Directory Structure
- `include/`: Public headers.
- `ai_inference.cpp`: Core inference task and TFLM logic.
- `ai_model_manager.c`: Model and metadata management.
- `ai_data_collector.c`: API for sensor data ingestion.
- `ai_ring_buffer.c`: Internal communication queue.

## Configuration
See `include/ai_config.h` for thresholds and dimensions.

## Documentation
For detailed technical information, refer to [docs/specs/ai_engine_technical_specification.md](../../../../docs/specs/ai_engine_technical_specification.md).
