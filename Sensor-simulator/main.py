import threading
import time
from core.sensors import Sensor
from core.registry import SensorRegistry
from protocols.modbus_server import run_modbus
from protocols.bacnet_server import run_bacnet
from protocols.mqtt_client import run_mqtt

registry = SensorRegistry()

registry.add(Sensor("temperature", "C", 22.0, -10, 50))
registry.add(Sensor("humidity", "%", 50.0, 0, 100))
registry.add(Sensor("pressure", "Pa", 101325, 98000, 105000))

def sensor_loop():
    while True:
        registry.update_all()
        time.sleep(1)

threading.Thread(target=sensor_loop, daemon=True).start()
threading.Thread(target=run_modbus, args=(registry,), daemon=True).start()
threading.Thread(target=run_bacnet, args=(registry,), daemon=True).start()
threading.Thread(target=run_mqtt, args=(registry,), daemon=True).start()

from api.server import run_api
threading.Thread(target=run_api, args=(registry,), daemon=True).start()

while True:
    time.sleep(10)
