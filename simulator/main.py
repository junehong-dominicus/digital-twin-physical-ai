import threading
import time
import os
import logging
import warnings
from dotenv import load_dotenv
import yaml

# Load environment variables
load_dotenv()

from core.sensors import Sensor
from core.registry import SensorRegistry
from core.simulation import start_simulation
from services.modbus_server import run_modbus
from services.bacnet_server import run_bacnet
from services.opcua_server import start_opcua
from services.enip_server import start_enip
from services.mqtt_client import run_mqtt, set_mqtt_enabled
from api.server import run_api

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
warnings.filterwarnings("ignore", message="no signal handlers for child threads")
logging.getLogger("pymodbus").setLevel(logging.WARNING)
logging.getLogger("bacpypes").setLevel(logging.WARNING)

def load_config(registry):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config", "sensors.yaml")
    
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
            for s in config.get("sensors", []):
                registry.add(Sensor(**s))
        logging.info(f"Loaded {len(registry.sensors)} sensors from {config_path}")
    else:
        logging.warning("Config file not found, using default sensors")
        registry.add(Sensor("temperature", "C", 22.0, -10, 50, writable=True))

def main():
    logging.info("Initializing Industrial Protocol Simulator...")
    registry = SensorRegistry()
    load_config(registry)

    # 1. Start core simulation
    start_simulation(registry)

    # 2. Start industrial protocol servers
    servers = [
        (run_modbus, "MODBUS_PORT", 5020, "Modbus"),
        (run_bacnet, "BACNET_PORT", 47808, "BACnet"),
        (start_opcua, "OPCUA_PORT", 4840, "OPC-UA"),
        (start_enip, "ENIP_PORT", 44818, "EtherNet/IP")
    ]

    for func, env_var, default, name in servers:
        port = int(os.getenv(env_var, default))
        logging.info(f"Starting {name} server on port {port}...")
        threading.Thread(target=func, args=(registry, port), daemon=True).start()

    # 3. Start MQTT Client
    mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
    mqtt_port = int(os.getenv("MQTT_PORT", 1883))
    set_mqtt_enabled(os.getenv("MQTT_ENABLED", "True").lower() == "true")
    threading.Thread(target=run_mqtt, args=(registry, mqtt_broker, mqtt_port), daemon=True).start()

    # 4. Start Dashboard API
    logging.info("Starting Dashboard API on port 8081...")
    run_api(registry) # This is blocking

if __name__ == "__main__":
    main()
