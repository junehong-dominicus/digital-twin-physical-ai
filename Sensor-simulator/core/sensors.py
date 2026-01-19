import random
import time
import math

class Sensor:
    def __init__(self, name, unit, base, min_v, max_v, noise=0.1, period=1.0, writable=True):
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
        self.writable = writable
        self.priority_array = [None] * 16

    def set_fault(self, fault_type, value=None):
        self.fault = {"type": fault_type, "value": value}

    def clear_fault(self):
        self.fault = None

    def set_priority(self, value, priority):
        """Set a value at a specific priority (1-16)."""
        if self.writable and 1 <= priority <= 16:
            self.priority_array[priority - 1] = value

    def clear_priority(self, priority):
        """Clear a value at a specific priority (1-16)."""
        if self.writable and 1 <= priority <= 16:
            self.priority_array[priority - 1] = None

    def update(self):
        # Check commandable priority first
        active_value = None
        for val in self.priority_array:
            if val is not None:
                active_value = val
                break
        
        if active_value is not None:
            self.value = active_value
            # If frozen, stick to frozen value? 
            # If fault is "freeze", it should probably override priority array?
            # Or priority array overrides simulation?
            # Let's say: fault overrides everything (physical failure simulation).
             
        t = time.time() - self.t0
        
        # Apply fault: Freeze
        if self.fault and self.fault["type"] == "freeze":
            if self.fault["value"] is not None:
                self.value = float(self.fault["value"])
            return self.value

        # If priority array active and NO freeze, use it.
        if active_value is not None:
             self.value = active_value
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
        self.priority_array = [None] * 16

    def set_priority(self, value, priority):
        """Set a value at a specific priority (1-16)."""
        if self.writable and 1 <= priority <= 16:
            self.priority_array[priority - 1] = value

    def clear_priority(self, priority):
        """Clear a value at a specific priority (1-16)."""
        if self.writable and 1 <= priority <= 16:
            self.priority_array[priority - 1] = None

    def update(self):
        # Check commandable priority
        active_value = None
        for val in self.priority_array:
            if val is not None:
                active_value = val
                break
        
        if active_value is not None:
            self.value = active_value
            # Apply faults on top of overridden value if needed? 
            # Usually strict override bypasses simulation, but faults act on the hardware reading?
            # If "software override", faults might not apply. 
            # If "hardware override", faults might apply.
            # For simplicity, priority array determines Present Value directly.
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
