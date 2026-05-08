import os
import argparse
import json
import time
import paho.mqtt.client as mqtt

import numpy as np

class FieldDataGenerator:
    def __init__(self, feature_dim=6):
        self.feature_dim = feature_dim
        # Vibration, Pressure, Smoke, Voltage, Flow, HeatRate
        self.base_values = [-17.8, 5.0, -4.0, -0.1, 2.0, 0.5] 
        self.noise_levels = [0.1, 1.0, 0.2, 0.01, 0.5, 0.05]

    def generate_sample(self, is_anomaly=False):
        sample = [v + np.random.normal(0, n) for v, n in zip(self.base_values, self.noise_levels)]
        if is_anomaly:
            # Inject a vibration spike (index 0)
            sample[0] += np.random.uniform(5, 10)
            # Inject smoke/heat spike (index 2 & 5)
            sample[2] += np.random.uniform(2, 5)
            sample[5] += np.random.uniform(1, 2)
        return sample

    def generate_normal(self, count=1000):
        return [self.generate_sample(is_anomaly=False) for _ in range(count)]

    def generate_anomalies(self, count=100):
        return [self.generate_sample(is_anomaly=True) for _ in range(count)]

def main():
    parser = argparse.ArgumentParser(description="Industrial Edge AI Field Data Injector")
    parser.add_argument("--broker", default="127.0.0.1", help="MQTT Broker IP")
    parser.add_argument("--node", default="node-ai-01", help="Node ID")
    parser.add_argument("--interval", type=float, default=1.0, help="Publish interval")
    parser.add_argument("--anomaly", action="store_true", help="Start with anomaly")
    args = parser.parse_args()

    client = mqtt.Client()
    try:
        client.connect(args.broker, 1883, 60)
        client.loop_start()
        print(f">>> Connected to {args.broker}. Injecting data for {args.node}...")
    except Exception as e:
        print(f"Error connecting to broker: {e}")
        return

    gen = FieldDataGenerator()
    is_anomaly = args.anomaly

    try:
        while True:
            sample = gen.generate_sample(is_anomaly)
            payload = {
                "timestamp": time.time(),
                "sensors": {
                    "vibration": round(sample[0], 3),
                    "pressure": round(sample[1], 2),
                    "smoke": round(sample[2], 3),
                    "voltage": round(sample[3], 4),
                    "flow": round(sample[4], 2),
                    "heat_rate": round(sample[5], 3)
                },
                "is_anomaly": is_anomaly
            }
            
            topic = f"dtpa/telemetry/ai/{args.node}"
            client.publish(topic, json.dumps(payload))
            
            print(f"[{time.strftime('%H:%M:%S')}] Published: Vib={payload['sensors']['vibration']} Smoke={payload['sensors']['smoke']} (Anomaly={is_anomaly})")
            time.sleep(args.interval)

            
    except KeyboardInterrupt:
        print("\nStopping injector...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
