import random
import time
import math

class Sensor:
    def __init__(self, name, unit, base, min, max, noise=0.1, period=1.0, writable=True, simulation_type="sine", **kwargs):
        self.name = name
        self.unit = unit
        self.base = base
        self.min = min
        self.max = max
        self.noise = noise
        self.period = period
        self.value = base
        self.t0 = time.time()
        self.fault = None
        self.writable = writable
        self.priority_array = [None] * 16
        self.simulation_type = simulation_type
        self.last_val = base

        # Capture extra args from config for specific simulation types
        self.spike_chance = kwargs.get("spike_chance", 0.05)
        self.spike_multiplier = kwargs.get("spike_multiplier", 1.5)
        self.pulse_width = kwargs.get("pulse_width", 1.0)

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

        val = self.base

        if self.simulation_type == "sine":
            drift = math.sin(t / 30.0) * (self.max - self.min) * 0.05
            val += drift
        elif self.simulation_type == "ramp":
            # Sawtooth pattern over 60 seconds
            progress = (t % 60.0) / 60.0
            val = self.min + (self.max - self.min) * progress
        elif self.simulation_type == "random_walk":
            # Random walk from last value
            step = random.uniform(-self.noise, self.noise)
            # Tendency to return to base if far away
            if self.last_val > self.base + (self.max - self.min)*0.2:
                step -= self.noise * 0.5
            elif self.last_val < self.base - (self.max - self.min)*0.2:
                step += self.noise * 0.5
            val = self.last_val + step
        elif self.simulation_type == "random_spike":
            # A base value that has some sine wave variation
            drift = math.sin(t / 60.0) * (self.max - self.min) * 0.1
            val += drift
            if random.random() < self.spike_chance:
                val *= self.spike_multiplier
        elif self.simulation_type == "random_binary":
            if random.random() < self.spike_chance:
                val = self.max
            else:
                val = self.min
            self.value = val
            return self.value
        elif self.simulation_type == "step":
            if int(t / 10.0) % 2 == 0:
                val = self.min
            else:
                val = self.max
            self.value = val
            return self.value
        elif self.simulation_type == "sawtooth":
            progress = (t % self.period) / self.period
            val = self.min + (self.max - self.min) * progress
        elif self.simulation_type == "square_wave":
            if (t % self.period) < (self.period / 2):
                val = self.max
            else:
                val = self.min
            self.value = val
            return self.value
        elif self.simulation_type == "triangle_wave":
            phase = t % self.period
            half_p = self.period / 2
            if phase < half_p:
                val = self.min + (self.max - self.min) * (phase / half_p)
            else:
                val = self.max - (self.max - self.min) * ((phase - half_p) / half_p)
        elif self.simulation_type == "pulse":
            if (t % self.period) < self.pulse_width:
                val = self.max
            else:
                val = self.min
            self.value = val
            return self.value

        noise = random.uniform(-self.noise, self.noise)
        
        # Apply fault: Noise
        if self.fault and self.fault["type"] == "noise":
            extra_noise = float(self.fault.get("value", 1.0))
            noise += random.uniform(-extra_noise, extra_noise)
        
        val += noise

        # Apply fault: Offset
        if self.fault and self.fault["type"] == "offset":
            val += float(self.fault.get("value", 0.0))

        # Apply fault: Spike
        if self.fault and self.fault["type"] == "spike":
             if random.random() < 0.05:
                 val += float(self.fault.get("value", (self.max - self.min)*0.5))
            
        self.value = max(self.min, min(self.max, val))

        if self.simulation_type == "random_walk":
            self.last_val = self.value

        return self.value

class BaseSensor:
    def __init__(self, name, unit=None, base=0, **kwargs):
        self.name = name
        self.unit = unit
        self.value = base
        self.last_update = time.time()
        self.protocols = kwargs.get("protocols", [])

    def update(self):
        pass

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
