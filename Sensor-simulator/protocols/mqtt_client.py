import json
import time
import paho.mqtt.client as mqtt

def run_mqtt(registry):
    client = mqtt.Client()
    client.connect("localhost", 1883, 60)
    client.loop_start()

    while True:
        snap = registry.snapshot()
        for k, v in snap.items():
            payload = {
                "value": round(v, 2),
                "timestamp": int(time.time())
            }
            client.publish(f"sim/building1/{k}", json.dumps(payload))
        time.sleep(1)
