## Sensor Simulator

Simulates industrial sensors over:
- Modbus TCP
- BACnet/IP (COV + WriteProperty)
- MQTT
- REST API & Web Dashboard

Features:
- YAML-configured sensors
- Writable setpoints
- Alarm/event simulation
- Load testing & CI
- Multiple simulation patterns (Sine, Ramp, Random Walk, Spikes, Waves, etc.)

### Simulation Types

The simulator supports various patterns for sensor values:
- `sine`: Sine wave with noise.
- `ramp`: Linear ramp.
- `random_walk`: Brownian motion.
- `random_spike`: Base value with occasional spikes.
- `random_binary`: Random boolean toggles.
- `step`: Toggles between min/max every 10s.
- `sawtooth`: Linear ramp resetting to min.
- `square_wave`: Toggles between min/max based on period.
- `triangle_wave`: Linear ramp up and down.
- `pulse`: Short high value pulse periodically.

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

### Generating Load Config

To generate a large configuration for load testing (e.g., 50 buildings):

1. Edit `config/generator_presets.yaml` to define templates and building count.
2. Run the generator:
   ```bash
   python generate_load_config.py
   ```
   This will overwrite `config/sensors.yaml`, `config/modbus_map.yaml`, `config/mqtt_map.yaml`, and `config/bacnet_map.yaml`.

### Run

```bash
pip install -r requirements.txt
python main.py
```
The dashboard is available at:
```
http://localhost:8000/dashboard
```


