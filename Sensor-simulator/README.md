## Sensor Simulator

Simulates industrial sensors over:
- Modbus TCP
- BACnet/IP (COV + WriteProperty)
- MQTT

Features:
- YAML-configured sensors
- Writable setpoints
- Alarm/event simulation
- Load testing & CI

### Configuration

Create a `.env` file based on `.env.example` to configure the simulator:

```bash
cp .env.example .env
```

Available settings:
- `MQTT_BROKER`: MQTT Broker address (default: localhost)
- `MQTT_PORT`: MQTT Broker port (default: 1883)
- `MQTT_ENABLED`: Enable/Disable MQTT publishing (True/False)
- `MODBUS_PORT`: Modbus TCP server port (default: 5020)
- `BACNET_PORT`: BACnet/IP server port (default: 47808)

### Run

```bash
pip install -r requirements.txt
python main.py
