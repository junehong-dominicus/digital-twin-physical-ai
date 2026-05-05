import yaml
from core.sensors import AnalogSensor, BinarySensor

def load_sensors(path, registry):
    with open(path) as f:
        cfg = yaml.safe_load(f)

    for s in cfg["sensors"]:
        if s["type"] == "analog":
            sensor = AnalogSensor(**s)
        else:
            sensor = BinarySensor(**s)
        registry.add(sensor)
