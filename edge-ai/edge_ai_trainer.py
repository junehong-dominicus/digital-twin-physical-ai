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
    
    with open('models/anomaly_detector.tflite', 'wb') as f:
        f.write(tflite_model)
    
    print(f"✓ Model saved to models/anomaly_detector.tflite ({len(tflite_model)/1024:.1f} KB)")

    # Save scaler parameters for use in firmware
    import joblib
    joblib.dump(scaler, 'models/scaler.joblib')
    print("✓ Scaler saved to models/scaler.joblib")

if __name__ == "__main__":
    train_and_export()
