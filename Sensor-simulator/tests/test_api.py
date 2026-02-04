from fastapi.testclient import TestClient
from api.server import app, set_registry
from core.registry import SensorRegistry
from core.sensors import Sensor
import pytest

@pytest.fixture
def api_context():
    # Setup registry
    registry = SensorRegistry()
    registry.add(Sensor("temp", "C", 20.0, 0, 100))
    set_registry(registry)
    client = TestClient(app)
    return client, registry

def test_list_sensors(api_context):
    client, _ = api_context
    response = client.get("/sensors")
    assert response.status_code == 200
    data = response.json()
    assert any(s["name"] == "temp" for s in data)

def test_get_sensor_details(api_context):
    client, _ = api_context
    response = client.get("/sensors/temp")
    assert response.status_code == 200
    assert response.json()["name"] == "temp"

def test_fault_injection_freeze(api_context):
    client, registry = api_context
    # Inject fault
    response = client.post("/sensors/temp/fault", json={"type": "freeze", "value": 50.0})
    assert response.status_code == 200
    
    # Force update to apply fault
    registry.get_sensor("temp").update()

    # Check sensor value
    response = client.get("/sensors/temp")
    assert response.json()["value"] == 50.0

def test_fault_clear(api_context):
    client, registry = api_context
    # Offset fault
    client.post("/sensors/temp/fault", json={"type": "offset", "value": 10.0})
    
    # Clear fault
    response = client.delete("/sensors/temp/fault")
    assert response.status_code == 200
    
    # Update
    registry.get_sensor("temp").update()

    # Check fault status
    response = client.get("/sensors/temp")
    assert response.json()["fault"] is None
