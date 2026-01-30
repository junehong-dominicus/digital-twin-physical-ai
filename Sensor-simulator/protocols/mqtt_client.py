import json
import time
import logging
import paho.mqtt.client as mqtt

MQTT_ENABLED = True

def set_mqtt_enabled(enabled: bool):
    global MQTT_ENABLED
    MQTT_ENABLED = enabled
    logging.info(f"MQTT Client {'enabled' if enabled else 'disabled'}")

def run_mqtt(registry, broker="localhost", port=1883):
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
            snap = registry.snapshot()
            for k, v in snap.items():
                payload = {
                    "value": round(v, 2),
                    "timestamp": int(time.time())
                }
                client.publish(f"sim/building1/{k}", json.dumps(payload))
        time.sleep(1)
