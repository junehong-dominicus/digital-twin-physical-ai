from threading import Lock

class SensorRegistry:
    def __init__(self):
        self.sensors = {}
        self.lock = Lock()

    def add(self, sensor):
        from models.industrial import FACPSensor, PumpController
        
        # Check if we should upgrade the sensor to a specialized model
        if hasattr(sensor, 'simulation_type'):
            if sensor.simulation_type == "facp":
                sensor = FACPSensor(sensor.name, **sensor.__dict__)
            elif sensor.simulation_type == "pump":
                sensor = PumpController(sensor.name, **sensor.__dict__)

        self.sensors[sensor.name] = sensor
        return sensor

    def update_all(self):
        with self.lock:
            for s in self.sensors.values():
                s.update()

    def get(self, name):
        with self.lock:
            return self.sensors[name].value

    def snapshot(self):
        with self.lock:
            return {k: v.value for k, v in self.sensors.items()}

    def by_bacnet_instance(self, instance):
        mapping = {1: "temperature", 2: "humidity", 3: "pressure"}
        name = mapping.get(instance)
        if name:
            return self.sensors.get(name)
        return None

    def get_sensor(self, name):
         return self.sensors.get(name)
