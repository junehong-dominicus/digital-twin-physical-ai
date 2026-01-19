### One sensor mode -> multiple protocol adapters
           ┌──────────────────────┐
           │   Sensor Simulator   │
           │  (virtual physics)   │
           └─────────┬────────────┘
                     │
     ┌───────────────┼────────────────┐
     │               │                │
┌────▼────┐     ┌────▼────┐     ┌─────▼─────┐
│ Modbus  │     │ BACnet  │     │   MQTT    │
│ RTU/TCP │     │ IP/MSTP │     │ Pub/Sub   │
└─────────┘     └─────────┘     └───────────┘

### Unified internal representation
```
typedef enum {
    SENSOR_TEMP,
    SENSOR_HUMIDITY,
    SENSOR_PRESSURE,
    SENSOR_GAS,
    SENSOR_WATER_QUALITY,
    SENSOR_MOTION,
    SENSOR_LEVEL,
    SENSOR_SMOKE,
    SENSOR_ACCEL,
    SENSOR_GYRO,
    SENSOR_IMAGE,
} sensor_type_t;

typedef struct {
    sensor_type_t type;
    float value;
    float min;
    float max;
    float noise;
    uint32_t update_ms;
} sensor_t;
```

### Sensor value generation (realistic)
Examples:
Temperature
```
value = base + sin(time) * drift + random_noise();
```

Motion
```
value = (rand() % 100 < 5) ? 1 : 0;
```

Gas / Smoke
```
value += leak_event ? rise_rate : decay_rate;
```

Accelerometer
```
ax = sin(t) * 0.02;
ay = cos(t) * 0.02;
az = 1.0;
```

### Protocol mapping
#### Modbus mapping
Register conventions
| Sensor      | Modbus object                 |
| ----------- | ----------------------------- |
| Temperature | Input Register (30001)        |
| Humidity    | Input Register (30002)        |
| Pressure    | Input Register (30003)        |
| Motion      | Discrete Input                |
| Smoke       | Discrete Input                |
| Level       | Holding Register              |
| Accel       | 3 consecutive Input Registers |
Float encoding
- IEEE-754
- Big endian or little endian selectable
Example:
```
30001–30002 → float temperature
30003–30004 → float humidity
```
#### BACnet mapping (building automation friendly)
Typical object mapping
| Sensor      | BACnet Object               |
| ----------- | --------------------------- |
| Temperature | Analog Input (AI)           |
| Humidity    | Analog Input (AI)           |
| Pressure    | Analog Input (AI)           |
| Motion      | Binary Input (BI)           |
| Smoke       | Binary Input (BI)           |
| Level       | Analog Input (AI)           |
| Image       | Device Object / proprietary |
Example:
```
AI-1  → Temperature
AI-2  → Humidity
BI-1  → Motion
BI-2  → Smoke
```
Properties:
- Present_Value
- Units
- Status_Flags
- Out_Of_Service

#### MQTT mapping
Topic structure (clean & scalable)
```
building/zone1/temp
building/zone1/humidity
building/zone1/gas/co2
building/zone1/motion
```
Payload (JSON or binary)
```
{
  "value": 23.7,
  "unit": "C",
  "timestamp": 1700000000
}
```
OR
```
23.7
```
#### Example simulator matrix
| Sensor   | Modbus | BACnet | MQTT |
| -------- | ------ | ------ | ---- |
| Temp     | IR     | AI     | ✔    |
| Humidity | IR     | AI     | ✔    |
| Pressure | IR     | AI     | ✔    |
| Gas      | IR     | AI     | ✔    |
| Motion   | DI     | BI     | ✔    |
| Smoke    | DI     | BI     | ✔    |
| Level    | HR     | AI     | ✔    |
| Accel    | IR x3  | AI x3  | ✔    |

#### Configuration
Use JSON / CLI / Web UI to define:
```
{
  "sensor": "temperature",
  "min": -10,
  "max": 50,
  "noise": 0.2,
  "update_ms": 1000,
  "protocols": ["modbus", "bacnet", "mqtt"]
}
```

#### Validation & testing
Test tools
- Modbus Poll / QModMaster
- YABE / BACnet Browser
- MQTT Explorer / Grafana
Scenarios
- Sensor drift
- Alarm thresholds
- Burst updates
- Network loss

#### Project structure
sensor-simulator/
├── core/
│   ├── sensors.py          # sensor physics & state
│   ├── registry.py         # global sensor table
├── protocols/
│   ├── modbus_server.py
│   ├── bacnet_server.py
│   ├── mqtt_client.py
├── config/
│   └── sensors.yaml
├── main.py
└── requirements.txt
