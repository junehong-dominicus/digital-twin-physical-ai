# Edge AI Training & Deployment Workflow

This guide outlines the end-to-end process for developing, optimizing, and deploying Machine Learning models to the Industrial Edge Gateway.

## 1. Data Acquisition
The firmware pipes 6 core features into the AI Engine. To train a model, you first need to collect high-fidelity historical data.

| Feature Index | Name | Unit | Description |
|---|---|---|---|
| 0 | Vibration | g | RMS Vibration level (Accelerometer) |
| 1 | Pressure | PSI | Industrial pump/pipe pressure |
| 2 | Smoke | % | Optical smoke obscuration |
| 3 | Voltage | V | System bus voltage (24V nominal) |
| 4 | Flow | GPM | Liquid flow rate (Sprinkler/Pump) |
| 5 | Heat Rate | °C/s | Rate of temperature change |

**Action**: Use the Digital Twin Dashboard to export CSV data from historical telemetry logs.

### Feature Engineering (Accuracy Boost)
Don't just use raw values. For industrial systems, **rates of change** and **moving averages** provide significantly better accuracy:
- **Rate of Change**: $\Delta Value / \Delta Time$ (e.g., Temperature Rate)
- **Moving Averages**: Smooth out sensor noise using a window of 3-5 samples.
- **Variance**: Use as a stability indicator to detect flickering sensors.

## 2. Model Development (Python/Keras)
For the ESP32-WROVER platform, we recommend two primary architectures:

### A. Anomaly Detection (Autoencoder)
*   **Goal**: Detect when sensor patterns deviate from the "Normal" baseline.
*   **Method**: Train the model only on "Normal" data. If the reconstruction error (loss) is high, it's an anomaly.
*   **Size**: Aim for < 100KB.

### B. Predictive Maintenance (GRU)
*   **Goal**: Predict the "Next State" of a sensor (e.g., Temp in 10 minutes).
*   **Method**: Use a Gated Recurrent Unit (GRU) for time-series forecasting.
*   **Size**: Aim for < 256KB.

### C. Binary Classification (Tiny Dense NN)
*   **Goal**: Direct event detection (e.g., Fire/Not Fire, Leak/No Leak).
*   **Method**: Simple 2-3 layer fully connected network.
*   **Size**: Extremely tiny (~2-10KB after quantization).

## 3. Dataset Design & Best Practices

### The "False Alarm" Class
When training, it is **critical** to include data for "False Alarm" scenarios. 
- *Example (Fire Detection)*: Include data for steam, cooking smoke, or heavy dust spikes labeled as "Normal" so the AI learns to ignore them.

### Data Balancing
Ensure your training set has a balanced mix of "Normal" vs "Event" data to prevent the model from becoming biased toward the most frequent class.

## 4. Implementation Examples

### Example: Training an Autoencoder for Anomaly Detection
The key idea is to train the model to "compress" and then "reconstruct" normal data. Anomaly detection happens when the model fails to reconstruct data it hasn't seen before.

```python
import tensorflow as tf
from tensorflow.keras import layers, losses

# 1. Define the Architecture
class AnomalyDetector(tf.keras.Model):
  def __init__(self):
    super(AnomalyDetector, self).__init__()
    self.encoder = tf.keras.Sequential([
      layers.Dense(32, activation="relu"),
      layers.Dense(16, activation="relu"),
      layers.Dense(8, activation="relu")]) # Latent space
    
    self.decoder = tf.keras.Sequential([
      layers.Dense(16, activation="relu"),
      layers.Dense(32, activation="relu"),
      layers.Dense(6, activation="sigmoid")]) # 6 output features

  def call(self, x):
    encoded = self.encoder(x)
    decoded = self.decoder(encoded)
    return decoded

# 2. Train the model
autoencoder = AnomalyDetector()
autoencoder.compile(optimizer='adam', loss='mae')

# Note: data_normal should be scaled between 0 and 1
autoencoder.fit(data_normal, data_normal, 
                epochs=50, 
                batch_size=32, 
                validation_split=0.1)
```

## 5. Optimization & Conversion
Standard TensorFlow models are too heavy for microcontrollers. You must use **TensorFlow Lite (TFLite)**.

### Conversion Script Template
```python
import tensorflow as tf

# 1. Load your Keras model
model = tf.keras.models.load_model('model_v1.h5')

# 2. Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# 3. Quantization (CRITICAL for ESP32)
# This reduces the model size by 4x and speeds up inference
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# 4. Target TFLite Micro compatibility
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]

tflite_model = converter.convert()

# 5. Save
with open('model.tflite', 'wb') as f:
    f.write(tflite_model)
```

## 6. Firmware Integration & Deployment

### Native Embedding (Production)
For high stability, the "Golden Model" is embedded directly into the firmware.
1.  **Convert TFLite to Header**:
    ```bash
    xxd -i model.tflite > anomaly_detector.h
    ```
2.  **Integrate**: Place in the `ai_engine` component directory. This ensures the model is always available upon boot.

### Deployment via OTA (Field Updates)
Field updates allow swapping models without flashing the entire firmware:

1.  **Connect**: Ensure the device is reachable via EHIF (Serial or Network).
2.  **Upload Model**:
    ```bash
    python model_ota_cli.py --file model.tflite --type 0 --target <IP>
    ```
3.  **Monitor**: The engine will automatically re-initialize upon receiving the new model.

## 7. Real-time Monitoring
Monitor the **Anomaly Score** (0.0 to 1.0) on the Digital Twin Dashboard.
- **Score < 0.65**: Normal operation.
- **Score 0.65 - 0.85**: Warning (Yellow) - Maintenance suggested.
- **Score > 0.85**: Alarm (Red) - Immediate inspection required.

## 8. Safety & Logic (The "Safety Gate")
AI should **NOT** directly trigger critical safety actions (like fire suppression). Use a multi-stage logic gate on the Master Controller:

```id="safety_logic"
IF (AI_Anomaly_Score > 0.85 AND Physical_Sensor_Threshold_Exceeded)
    → TRIGGER CRITICAL ALARM
ELSE
    → LOG WARNING AND MONITOR
```
*Note: This prevents AI "hallucinations" or edge-case misclassifications from causing expensive false shutdowns.*
wns.*
