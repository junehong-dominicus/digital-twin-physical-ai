import json
import time
import logging
import os
import yaml
import paho.mqtt.client as mqtt

MQTT_ENABLED = True

def set_mqtt_enabled(enabled: bool):
    global MQTT_ENABLED
    MQTT_ENABLED = enabled
    logging.info(f"MQTT Client {'enabled' if enabled else 'disabled'}")

def run_mqtt(registry, broker="localhost", port=1883, map_path="config/mqtt_map.yaml"):
    # Load MQTT topic map
    topic_map = {}
    if os.path.exists(map_path):
        with open(map_path, "r") as f:
            config = yaml.safe_load(f)
            topic_map = config.get("topics", {})
        logging.info(f"Loaded MQTT topic map from {map_path}")
    else:
        logging.warning(f"MQTT map file not found at {map_path}. No topics will be published.")

    client = mqtt.Client()
    try:
        client.connect(broker, port, 60)
        client.loop_start()
        logging.info(f"Connected to MQTT broker at {broker}:{port}")
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker: {e}")
        return

    while True:
        if MQTT_ENABLED:
            published_count = 0
            snapshot = registry.snapshot()
            for sensor_name, value in snapshot.items():
                topic = topic_map.get(sensor_name)
                if topic:
                    payload = {
                        "value": round(value, 2),
                        "timestamp": int(time.time())
                    }
                    client.publish(topic, json.dumps(payload))
                    published_count += 1
            # Use debug level to avoid flooding logs during normal operation
            logging.debug(f"MQTT publish loop: Published {published_count}/{len(snapshot)} sensor values.")
        time.sleep(1)
