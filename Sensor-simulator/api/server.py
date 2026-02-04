from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn
import os
import yaml

app = FastAPI()
_registry = None
_protocols_cache = {}

@app.get("/")
def read_root():
    count = len(_registry.sensors) if _registry else 0
    return {"status": "online", "sensor_count": count}

@app.get("/sensors/{sensor_name}")
def read_sensor(sensor_name: str):
    if _registry is None:
        raise HTTPException(status_code=503, detail="Registry not initialized")
    
    sensor = _registry.get_sensor(sensor_name)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    return {
        "name": sensor.name,
        "value": sensor.value,
        "unit": sensor.unit,
        "fault": sensor.fault
    }

def load_protocols():
    global _protocols_cache
    _protocols_cache.clear()
    
    # Modbus
    if os.path.exists("config/modbus_map.yaml"):
        try:
            with open("config/modbus_map.yaml", "r") as f:
                modbus = yaml.safe_load(f) or {}
                for section_name, section in modbus.items():
                    if isinstance(section, dict):
                        for addr, item in section.items():
                            name = item.get("sensor")
                            if name:
                                protos = _protocols_cache.setdefault(name, [])
                                type_map = {
                                    "holding_registers": "HR",
                                    "input_registers": "IR",
                                    "discrete_inputs": "DI",
                                    "coils": "CO"
                                }
                                prefix = type_map.get(section_name, section_name)
                                label = f"Modbus {prefix}:{addr}"
                                if label not in protos:
                                    protos.append(label)
        except Exception as e:
            print(f"Error loading modbus map: {e}")

    # BACnet
    if os.path.exists("config/bacnet_map.yaml"):
        try:
            with open("config/bacnet_map.yaml", "r") as f:
                bacnet = yaml.safe_load(f) or {}
                for obj_type, objects in bacnet.items():
                    if isinstance(objects, dict):
                        for instance, data in objects.items():
                            name = data.get("sensor")
                            if name:
                                protos = _protocols_cache.setdefault(name, [])
                                type_map = {
                                    "analogValue": "AV",
                                    "binaryValue": "BV",
                                    "analogInput": "AI",
                                    "binaryInput": "BI",
                                    "multiStateValue": "MSV"
                                }
                                prefix = type_map.get(obj_type, obj_type)
                                label = f"BACnet {prefix}:{instance}"
                                if label not in protos:
                                    protos.append(label)
        except Exception as e:
            print(f"Error loading bacnet map: {e}")

@app.get("/sensors")
def list_sensors():
    if _registry is None:
        return []
    
    if not _protocols_cache:
        load_protocols()

    sensors_list = []
    # Iterate over a copy of values to avoid runtime error if dict changes size
    for s in list(_registry.sensors.values()):
        sensors_list.append({
            "name": s.name,
            "value": s.value,
            "unit": s.unit,
            "writable": s.writable,
            "type": getattr(s, "simulation_type", "unknown"),
            "protocols": _protocols_cache.get(s.name, []),
            "fault": s.fault
        })
    return sorted(sensors_list, key=lambda x: x["name"])

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    if os.path.exists(html_path):
        with open(html_path, "r") as f:
            return f.read()
    return "Dashboard file not found."

class FaultInjection(BaseModel):
    type: str
    value: float

@app.post("/sensors/{sensor_name}/fault")
def inject_fault(sensor_name: str, fault: FaultInjection):
    if _registry is None:
        raise HTTPException(status_code=503, detail="Registry not initialized")
    
    sensor = _registry.get_sensor(sensor_name)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    sensor.fault = {"type": fault.type, "value": fault.value}
    return {"status": "success", "name": sensor.name, "message": f"Fault {fault.type} injected"}

@app.delete("/sensors/{sensor_name}/fault")
def clear_fault(sensor_name: str):
    if _registry is None:
        raise HTTPException(status_code=503, detail="Registry not initialized")
    
    sensor = _registry.get_sensor(sensor_name)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    sensor.fault = None
    return {"status": "success", "name": sensor.name, "message": "Fault cleared"}

class SensorUpdate(BaseModel):
    value: float
    priority: int = Field(16, ge=1, le=16)

@app.post("/sensors/{sensor_name}")
def update_sensor(sensor_name: str, update: SensorUpdate):
    if _registry is None:
        raise HTTPException(status_code=503, detail="Registry not initialized")
    
    sensor = _registry.get_sensor(sensor_name)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    if not sensor.writable:
        raise HTTPException(status_code=400, detail="Sensor is not writable")
    
    sensor.set_priority(update.value, update.priority)
    return {"status": "success", "name": sensor.name, "message": "Setpoint updated"}

def set_registry(registry):
    global _registry
    _registry = registry

def run_api(registry):
    global _registry
    _registry = registry
    # Configure uvicorn to run in a thread without signal handlers
    port = int(os.getenv("SIM_PORT", 8080)) # Use a different default to avoid conflict
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None
    server.run()