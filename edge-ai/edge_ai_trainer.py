import os
# Force Legacy Keras to avoid Keras 3 introspection bugs in TF 2.18 + Python 3.12
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, losses
from sklearn.preprocessing import MinMaxScaler
from field_data_generator import FieldDataGenerator

# ─────────────────────────────────────────────────────────────────────────────
# 1. MODEL ARCHITECTURES
# ─────────────────────────────────────────────────────────────────────────────

def create_anomaly_detector(input_dim=6):
    """
    Autoencoder for detecting anomalies in industrial sensor data.
    Goal: < 100KB footprint on ESP32.
    Using Sequential API for maximum TFLite compatibility.
    """
    model = tf.keras.Sequential([
        layers.Input(shape=(input_dim,)),
        layers.Dense(32, activation="relu"),
        layers.Dense(16, activation="relu"),
        layers.Dense(8, activation="relu"), # Latent space
        layers.Dense(16, activation="relu"),
        layers.Dense(32, activation="relu"),
        layers.Dense(input_dim, activation="sigmoid")
    ], name="anomaly_detector")
    
    model.compile(optimizer='adam', loss='mae')
    return model

def create_predictive_gru(window_size=20, feature_dim=6):
    """
    GRU model for time-series forecasting.
    Predicts the next temperature value.
    """
    model = tf.keras.Sequential([
        layers.Input(shape=(window_size, feature_dim)),
        layers.GRU(32, return_sequences=False),
        layers.Dense(16, activation='relu'),
        layers.Dense(1) # Predict Temperature (index 2)
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

# ─────────────────────────────────────────────────────────────────────────────
# 2. DATA PREPARATION
# ─────────────────────────────────────────────────────────────────────────────

def prepare_data():
    gen = FieldDataGenerator()
    
    # Generate 5000 normal samples for training
    raw_data = gen.generate_normal(5000)
    data = np.array(raw_data)
    
    # Scale data to [0, 1] as required by Autoencoder (sigmoid output)
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)
    
    return scaled_data, scaler

# ─────────────────────────────────────────────────────────────────────────────
# 3. TRAINING & CONVERSION
# ─────────────────────────────────────────────────────────────────────────────

def export_to_header(tflite_model, scaler, header_path):
    """
    Converts TFLite model and normalization metadata into a C header file.
    """
    print(f">>> Exporting C header to {header_path}...")
    
    # 1. Prepare Normalization Metadata
    # Scaler min/max for each feature
    mins = scaler.data_min_
    maxs = scaler.data_max_
    
    with open(header_path, 'w') as f:
        f.write("/* Auto-generated Edge AI Model Header */\n")
        f.write("#ifndef ANOMALY_DETECTOR_H\n")
        f.write("#define ANOMALY_DETECTOR_H\n\n")
        
        # Write Normalization Data
        f.write("// Normalization Metadata (Min/Max values from training set)\n")
        f.write("typedef struct {\n    float min;\n    float max;\n} feature_norm_entry_t;\n\n")
        f.write(f"const feature_norm_entry_t ANOMALY_MODEL_NORMS[{len(mins)}] = {{\n")
        for m_min, m_max in zip(mins, maxs):
            f.write(f"    {{ {m_min:.6f}f, {m_max:.6f}f }},\n")
        f.write("};\n\n")
        
        # Write TFLite Model Array
        f.write(f"const unsigned char anomaly_detector_tflite[] = {{\n    ")
        for i, byte in enumerate(tflite_model):
            f.write(f"0x{byte:02x}, ")
            if (i + 1) % 12 == 0:
                f.write("\n    ")
        f.write("\n};\n\n")
        f.write(f"const unsigned int anomaly_detector_tflite_len = {len(tflite_model)};\n\n")
        
        f.write("#endif // ANOMALY_DETECTOR_H\n")

def train_and_export():
    print(">>> Generating synthetic field data...")
    data_train, scaler = prepare_data()
    
    # --- A. Train Anomaly Detector (Autoencoder) ---
    print("\n>>> Training Anomaly Detector (Autoencoder)...")
    autoencoder = create_anomaly_detector(input_dim=6)
    
    # Train only on normal data
    autoencoder.fit(data_train, data_train, 
                    epochs=20, 
                    batch_size=32, 
                    validation_split=0.1,
                    verbose=1)
    
    # Save the full model
    if not os.path.exists('models'): os.makedirs('models')
    
    # --- B. Export to TFLite (Quantized) ---
    print("\n>>> Converting to TFLite (ESP32 Ready)...")
    
    # Get concrete function to bypass broken Keras/TFLite bridge in TF 2.18
    run_model = tf.function(lambda x: autoencoder(x))
    concrete_func = run_model.get_concrete_function(
        tf.TensorSpec([None, 6], tf.float32)
    )
    
    converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    
    # Save .tflite
    tflite_path = 'models/anomaly_detector.tflite'
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)
    print(f"SUCCESS: Model saved to {tflite_path} ({len(tflite_model)/1024:.1f} KB)")

    # Save .h (New!)
    # 1. Local copy for reference
    local_header = 'models/anomaly_detector.h'
    export_to_header(tflite_model, scaler, local_header)
    
    # 2. Firmware copy for direct build integration
    firmware_header = '../firmware/protocol_node/components/ai_engine/include/anomaly_detector.h'
    if os.path.exists(os.path.dirname(firmware_header)):
        export_to_header(tflite_model, scaler, firmware_header)
        print(f"SUCCESS: Synchronized header to firmware: {firmware_header}")

    # Save scaler parameters for use in Python environments
    import joblib
    joblib.dump(scaler, 'models/scaler.joblib')
    print("SUCCESS: Scaler saved to models/scaler.joblib")

if __name__ == "__main__":
    train_and_export()
