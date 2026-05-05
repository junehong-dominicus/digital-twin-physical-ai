import random
import time
from enum import IntEnum
from core.sensors import Sensor

class FACPStatus(IntEnum):
    NORMAL = 0
    ALARM = 1
    TROUBLE = 2
    SUPERVISORY = 3
    TEST = 4

class FACPSensor(Sensor):
    """
    Advanced Fire Alarm Control Panel (FACP) simulation.
    Includes state machine and multi-register feedback.
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, unit="state", base=0, min=0, max=4, writable=True, simulation_type="facp", **kwargs)
        self.state = FACPStatus.NORMAL
        self.last_event = "System Initialized"
        self.active_zones = []

    def update(self):
        # 1. Handle overrides first (priority array)
        super().update()
        
        # 2. State Machine Logic
        # If value is forced via API/Simulator, update internal state
        self.state = FACPStatus(int(self.value))

        # 3. Random event simulation if in normal mode
        if self.state == FACPStatus.NORMAL:
            if random.random() < 0.001: # Rare fire alarm
                self.set_priority(FACPStatus.ALARM, 1) # Internal override
                self.last_event = "SMOKE DETECTED - ZONE 4"
                self.active_zones = [4]
            elif random.random() < 0.005: # Sensor trouble
                self.state = FACPStatus.TROUBLE
                self.last_event = "COMM LOSS - DETECTOR 12"
        
        return self.value

class PumpController(Sensor):
    """
    Industrial Pump Controller with pressure/flow correlation.
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, unit="RPM", base=0, min=0, max=3600, writable=True, simulation_type="pump", **kwargs)
        self.pressure = 0.0
        self.flow = 0.0
        self.efficiency = 0.95

    def update(self):
        super().update()
        # Physics correlation: Pressure is proportional to RPM squared
        rpm_norm = self.value / self.max
        self.pressure = (rpm_norm ** 2) * 100.0 # 0-100 PSI
        self.flow = rpm_norm * 500.0 # 0-500 GPM
        
        # Add some noise
        self.pressure += random.uniform(-0.5, 0.5)
        self.flow += random.uniform(-1.0, 1.0)
        
        return self.value
