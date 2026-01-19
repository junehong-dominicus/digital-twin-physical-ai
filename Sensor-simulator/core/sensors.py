import random
import time
import math

class Sensor:
    def __init__(self, name, unit, base, min_v, max_v, noise=0.1, period=1.0):
        self.name = name
        self.unit = unit
        self.base = base
        self.min = min_v
        self.max = max_v
        self.noise = noise
        self.period = period
        self.value = base
        self.t0 = time.time()
        self.fault = None

    def set_fault(self, fault_type, value=None):
        self.fault = {"type": fault_type, "value": value}

    def clear_fault(self):
        self.fault = None

    def update(self):
        t = time.time() - self.t0
        
        # Apply fault: Freeze
        if self.fault and self.fault["type"] == "freeze":
            if self.fault["value"] is not None:
                self.value = float(self.fault["value"])
            return self.value

        drift = math.sin(t / 30.0) * (self.max - self.min) * 0.05
        noise = random.uniform(-self.noise, self.noise)
        
        # Apply fault: Noise
        if self.fault and self.fault["type"] == "noise":
            extra_noise = float(self.fault.get("value", 1.0))
            noise += random.uniform(-extra_noise, extra_noise)
            
        val = self.base + drift + noise
        
        # Apply fault: Offset
        if self.fault and self.fault["type"] == "offset":
            val += float(self.fault.get("value", 0.0))
            
        self.value = max(self.min, min(self.max, val))
        return self.value

class BaseSensor:
    def __init__(self, name, unit=None, base=0, **kwargs):
        self.name = name
        self.unit = unit
        self.value = base
        self.last_update = time.time()
        self.protocols = kwargs.get("protocols", [])

class AnalogSensor(BaseSensor):
    def __init__(self, writable=False, **kw):
        super().__init__(**kw)
        self.writable = writable
        self.override = None

    def set_override(self, value):
        if self.writable:
            self.override = value

    def update(self):
        if self.override is not None:
            self.value = self.override
            return
        super().update()


class BinarySensor(BaseSensor):
    def __init__(self, alarm=None, **kw):
        super().__init__(**kw)
        self.alarm = alarm

    def update(self):
        if self.alarm and random.random() < self.alarm["trigger_probability"]:
            self.value = 1
        else:
            self.value = 0
