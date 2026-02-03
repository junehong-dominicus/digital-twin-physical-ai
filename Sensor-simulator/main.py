import threading
import time
import os
import logging
from dotenv import load_dotenv
import yaml
import warnings

load_dotenv()

from core.sensors import Sensor
from core.registry import SensorRegistry
from protocols.modbus_server import run_modbus
from protocols.bacnet_server import run_bacnet
from protocols.mqtt_client import run_mqtt, set_mqtt_enabled

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress bacpypes thread warning
warnings.filterwarnings("ignore", message="no signal handlers for child threads")

# Reduce noise from protocol libraries
logging.getLogger("pymodbus").setLevel(logging.WARNING)
logging.getLogger("bacpypes").setLevel(logging.WARNING)

try:
    registry = SensorRegistry()

    config_path = "config/sensors.yaml"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            for s in config.get("sensors", []):
                registry.add(Sensor(**s))
        logging.info(f"Loaded {len(registry.sensors)} sensors from {config_path}")
        if len(registry.sensors) < 10:
            logging.debug(f"Loaded sensor names: {list(registry.sensors.keys())}")
    else:
        logging.info("Config file not found, using default sensors")
        registry.add(Sensor("temperature", "C", 22.0, -10, 50, writable=True))
        registry.add(Sensor("humidity", "%", 50.0, 0, 100, writable=True))
        registry.add(Sensor("pressure", "Pa", 101325, 98000, 105000, writable=True))
except Exception as e:
    with open("startup_error.log", "a") as f:
        f.write(f"Registry initialization error: {e}\n")
    raise

def sensor_loop():
    # Track previous values to log changes only
    prev_values = {}
    while True:
        registry.update_all()
        
        # Verification: Log specific binary sensors when they change
        for name in ["building_1_motion", "building_1_fire_alarm"]:
            sensor = registry.get_sensor(name)
            if sensor:
                val = sensor.value
                if prev_values.get(name) != val:
                    logging.info(f"[VERIFY] {name} toggled to {val}")
                    prev_values[name] = val

        time.sleep(1)

threading.Thread(target=sensor_loop, daemon=True).start()
modbus_port = int(os.getenv("MODBUS_PORT", 5020))
threading.Thread(target=run_modbus, args=(registry, modbus_port), daemon=True).start()
bacnet_port = int(os.getenv("BACNET_PORT", 47808))
threading.Thread(target=run_bacnet, args=(registry, bacnet_port), daemon=True).start()

# MQTT Client setup
mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
mqtt_port = int(os.getenv("MQTT_PORT", 1883))
mqtt_enabled = os.getenv("MQTT_ENABLED", "True").lower() == "true"
set_mqtt_enabled(mqtt_enabled)
threading.Thread(target=run_mqtt, args=(registry, mqtt_broker, mqtt_port), daemon=True).start()

from api.server import run_api
threading.Thread(target=run_api, args=(registry,), daemon=True).start()

while True:
    time.sleep(10)
