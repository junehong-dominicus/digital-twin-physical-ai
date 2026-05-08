# Edge AI Tooling & ML Ops

This directory contains the Python-based machine learning pipeline for the Digital Twin Physical AI platform. It handles data generation, model training, and Over-The-Air (OTA) deployment to the firmware's AI Engine.

## 🚀 Quick Start

### 1. Setup Environment
We recommend using `uv` or `venv`:
```bash
# Using uv
uv sync

# Using pip
pip install -r requirements.txt
```

### 2. Generate Data & Train Model
The trainer script automatically generates synthetic industrial data and produces an optimized TFLite model:
```bash
python edge_ai_trainer.py
```
Outputs will be saved in the `models/` directory:
- `models/anomaly_detector.tflite`: Quantized model for ESP32.
- `models/scaler.joblib`: Normalization parameters for the Python environment.

### 3. Inject Live Data for Testing
Simulate a running machine by injecting data into your MQTT broker:
```bash
# Normal data
python field_data_generator.py --broker localhost --interval 0.5

# Anomaly data (injects vibration and heat spikes)
python field_data_generator.py --broker localhost --anomaly
```

### 4. Deploy Model (OTA)
Push a new model to a running device without re-flashing:
```bash
# Via Serial
python model_ota_cli.py --mode serial --port COM3 --file models/anomaly_detector.tflite

# Via MQTT
python model_ota_cli.py --mode mqtt --broker 192.168.1.50 --file models/anomaly_detector.tflite
```

---

## 🛠️ Tool Descriptions

### [edge_ai_trainer.py](edge_ai_trainer.py)
The core ML pipeline.
- **Autoencoder (MLP)**: Default architecture for unsupervised anomaly detection.
- **GRU**: Recurrent architecture for time-series forecasting.
- **Quantization**: Automatically applies `INT8` quantization for efficient MCU execution.

### [field_data_generator.py](field_data_generator.py)
Industrial sensor simulator.
- **Features**: Vibration (g), Pressure (PSI), Smoke (%), Voltage (V), Flow (GPM), Heat Rate (°C/s).
- **Modes**: Library use for training datasets or standalone MQTT publisher for system testing.

### [model_ota_cli.py](model_ota_cli.py)
Deployment tool implementing the EHIF Model Update protocol.
- **Chunking**: Splits large models into 256/512 byte packets.
- **Verification**: Uses START/DATA/END sequence to ensure atomic updates on the device.

---

## 📖 Detailed Guides
- [Edge AI Workflow & Best Practices](EDGE_AI_WORKFLOW.md)
- [Firmware AI Engine Documentation](../docs/specs/ai_engine_technical_specification.md)
