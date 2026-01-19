from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
import uvicorn
import threading

app = FastAPI(title="Sensor Simulator API")

# Global registry reference
_registry = None

def set_registry(registry):
    global _registry
    _registry = registry

class FaultRequest(BaseModel):
    type: Literal["freeze", "offset", "noise"]
    value: Optional[float] = None

@app.get("/sensors")
def get_sensors():
    if not _registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")
    return _registry.sensors

@app.get("/sensors/{sensor_id}")
def get_sensor(sensor_id: str):
    if not _registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")
    sensor = _registry.get_sensor(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return {
        "id": sensor.name, 
        "value": sensor.value, 
        "unit": sensor.unit,
        "fault": sensor.fault
    }

@app.post("/sensors/{sensor_id}/fault")
def inject_fault(sensor_id: str, fault: FaultRequest):
    if not _registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")
    sensor = _registry.get_sensor(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    sensor.set_fault(fault.type, fault.value)
    return {"status": "fault injected", "sensor": sensor_id, "fault": sensor.fault}

@app.delete("/sensors/{sensor_id}/fault")
def clear_fault(sensor_id: str):
    if not _registry:
        raise HTTPException(status_code=503, detail="Registry not initialized")
    sensor = _registry.get_sensor(sensor_id)
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    
    sensor.clear_fault()
    return {"status": "fault cleared", "sensor": sensor_id}

def run_api(registry, host="0.0.0.0", port=8000):
    set_registry(registry)
    uvicorn.run(app, host=host, port=port, log_level="info")
