from threading import Lock

class SensorRegistry:
    def __init__(self):
        self.sensors = {}
        self.lock = Lock()

    def add(self, sensor):
        self.sensors[sensor.name] = sensor

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
        # ... logic if needed or removed ...
        pass

    def get_sensor(self, name):
         return self.sensors.get(name)
