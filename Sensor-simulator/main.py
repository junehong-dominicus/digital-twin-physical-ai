import threading
import time
import os
import logging
from dotenv import load_dotenv
import yaml

load_dotenv()

from core.sensors import Sensor
from core.registry import SensorRegistry
from protocols.modbus_server import run_modbus
from protocols.bacnet_server import run_bacnet
from protocols.mqtt_client import run_mqtt, set_mqtt_enabled

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    registry = SensorRegistry()

    config_path = "config/sensors.yaml"
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            for s in config.get("sensors", []):
                registry.add(Sensor(
                    name=s["name"],
                    unit=s.get("unit", ""),
                    base=s.get("base", 0.0),
                    min_v=s.get("min", 0.0),
                    max_v=s.get("max", 100.0),
                    noise=s.get("noise", 0.1),
                    period=s.get("period", 1.0),
                    writable=s.get("writable", True),
                    simulation_type=s.get("simulation_type", "sine")
                ))
        logging.info(f"Loaded sensors from {config_path}")
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
    while True:
        registry.update_all()
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
