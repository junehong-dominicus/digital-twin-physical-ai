# Edge AI Training & Deployment Workflow

This guide outlines the end-to-end process for developing, optimizing, and deploying Machine Learning models to the Industrial Edge Gateway.

## 1. Data Acquisition & Feature Map

The AI Engine processes a fixed **6-dimensional feature vector**. Whether using synthetic data or field telemetry, the following index mapping must be maintained:

| Index | Name | Unit | Target Nominal | Description |
|---|---|---|---|---|
| 0 | Vibration | g | -17.8 | RMS Vibration level (Accelerometer) |
| 1 | Pressure | PSI | 5.0 | Industrial pump/pipe pressure |
| 2 | Smoke | % | -4.0 | Optical smoke obscuration |
| 3 | Voltage | V | -0.1 | System bus voltage (24V nominal, relative) |
| 4 | Flow | GPM | 2.0 | Liquid flow rate (Sprinkler/Pump) |
| 5 | Heat Rate | °C/s | 0.5 | Rate of temperature change |

### Data Generation for Training
Use the `edge_ai_trainer.py` script to generate 5000+ normal samples. This creates a "baseline of normalcy" for the Autoencoder.

## 2. Model Development (Python/Keras)

We use **TensorFlow 2.18** with Legacy Keras support for the ESP32-S3 platform.

### A. Anomaly Detection (Autoencoder)
- **Architecture**: [6] -> [32] -> [16] -> [8] -> [16] -> [32] -> [6]
- **Goal**: Minimize reconstruction error on normal data.
- **Output**: Sigmoid activation ensures outputs are within [0, 1].

### B. Predictive Maintenance (GRU)
- **Architecture**: GRU(32) -> Dense(16) -> Dense(1)
- **Goal**: Predict the next value of a specific feature (default: Temperature/Heat Rate).
- **Sequence Length**: 10-20 steps.

## 3. Optimization & Conversion

To run on microcontrollers, models must be converted to **TFLite INT8 Quantized** format.

### Conversion Steps in `edge_ai_trainer.py`:
1.  **Concrete Function Extraction**: Bypasses Keras 3 bridge issues.
2.  **Default Optimization**: `tf.lite.Optimize.DEFAULT` for weight quantization.
3.  **TFLite Micro Target**: Ensures ops are supported by the ESP32 TFLM kernel.

## 4. Deployment via EHIF OTA

The `model_ota_cli.py` tool uses a 3-stage protocol to update models in the field:

### The OTA Protocol (EHIF)
1.  **START (0xA3)**: Initiates the update. Payload includes `type` (0 for model, 1 for metadata).
2.  **DATA (0xA4)**: Chunks of the file. Device writes these to a secondary NVS partition or PSRAM buffer.
3.  **END (0xA5)**: Finalizes the update. Triggers the AI Engine to reload the interpreter.

### CLI Usage:
```bash
python model_ota_cli.py --file models/anomaly_detector.tflite --mode mqtt --broker localhost
```

## 5. Monitoring & Safety Logic

Monitor the **Anomaly Score** (0.0 to 1.0) via the Dashboard or MQTT topic `dtpa/telemetry/ai/<node_id>`.

| Score | Status | Recommended Action |
|---|---|---|
| < 0.65 | Normal | None |
| 0.65 - 0.85 | Warning | Schedule maintenance check. |
| > 0.85 | Alarm | Immediate inspection; check physical failsafes. |

> [!IMPORTANT]
> **Safety Gate Rule**: AI anomalies should be treated as "Early Warnings." Never trigger critical shutdown sequences based on AI alone. Always verify against physical sensor trip points.

```id="safety_logic"
IF (AI_Anomaly_Score > 0.85 AND Physical_Sensor_Alert == TRUE)
    → TRIGGER CRITICAL RESPONSE
ELSE IF (AI_Anomaly_Score > 0.85)
    → LOG HIGH-PRIORITY MAINTENANCE TICKET
```
