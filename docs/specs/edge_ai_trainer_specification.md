# Edge AI Trainer - Technical Specification

The `edge_ai_trainer.py` script is the core of the ML Ops pipeline for the Digital Twin Physical AI platform. It automates the transition from synthetic data generation to firmware-ready TFLite models.

## 1. Overview
The trainer performs three primary roles:
*   **Synthetic Data Generation**: Creates 6-dimensional industrial sensor data using the `FieldDataGenerator`.
*   **Model Training**: Trains an Unsupervised Autoencoder for anomaly detection.
*   **Artifact Deployment**: Quantizes the model to `INT8`, converts it to a C header, and synchronizes it with the firmware build directory.

## 2. Model Architecture
### Anomaly Detector (Autoencoder)
The default architecture is a Multi-Layer Perceptron (MLP) Autoencoder designed for efficiency on ESP32-S3.
*   **Input Layer**: 6 features (Vibration, Pressure, Smoke, Voltage, Flow, HeatRate).
*   **Encoder**: 32 → 16 → 8 (Latent Space).
*   **Decoder**: 8 → 16 → 32 → 6 (Reconstruction).
*   **Activation**: `ReLU` for hidden layers, `Sigmoid` for the output layer to match normalized [0, 1] data.
*   **Loss Function**: Mean Absolute Error (MAE).

## 3. Data Pipeline
1.  **Generation**: Produces 5,000 "normal" samples to define the baseline behavior.
2.  **Scaling**: Uses `MinMaxScaler` to normalize features into the `[0, 1]` range.
3.  **Metadata Preservation**: Scaler min/max values are saved to `models/scaler.joblib` and exported to the C header to ensure consistency during real-time inference on the device.

## 4. TFLite Conversion & Quantization
To fit within the memory constraints of the ESP32-S3 (~100KB target for the AI engine):
*   **Concrete Function Extraction**: Uses TensorFlow's `get_concrete_function` to ensure stable conversion.
*   **Dynamic Range Quantization**: Applies `tf.lite.Optimize.DEFAULT` to reduce model size by ~4x with minimal accuracy loss.
*   **Output**: Produces a `~10 KB` binary model.

## 5. Firmware Integration
The script generates `anomaly_detector.h`, which contains:
*   **Normalization Structs**: A `feature_norm_entry_t` array mapping index to `min` and `max` values.
*   **Model Binary**: The TFLite model as a `const unsigned char` array.
*   **Automation**: Automatically detects the firmware directory structure and copies the header to `firmware/protocol_node/components/ai_engine/include/`.

## 6. Usage
### Basic Training
```bash
uv run edge_ai_trainer.py
```
### Environment Requirements
*   `tensorflow-cpu`: Lightweight version for training.
*   `scikit-learn`: For data scaling.
*   `joblib`: For metadata persistence.

## 7. Troubleshooting
*   **Slow Imports**: On Windows, the first import of TensorFlow may take 10-20 seconds.
*   **Encoding Issues**: The script uses ASCII-only logging to remain compatible with all terminal types.
