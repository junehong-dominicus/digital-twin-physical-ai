# Digital Twin Physical AI

This repository contains a professional, industrial-grade Digital Twin platform integrated with Edge AI (Edgie AI) and a Cognitive Layer for autonomous reasoning.

## 📁 Repository Structure

### [backend/](file:///c:/Project/AIoT/digital-twin-physical-ai/backend/)
- **[core/](file:///c:/Project/AIoT/digital-twin-physical-ai/backend/core/)**: The brain of the twin. Contains `twin_state.py` (Central State) and `cognitive_layer.py` (LLM Reasoning).
- **[api/](file:///c:/Project/AIoT/digital-twin-physical-ai/backend/api/)**: FastAPI application for serving telemetry and dashboard data.
- **[database/](file:///c:/Project/AIoT/digital-twin-physical-ai/backend/database/)**: SQL schema and migration scripts.

### [firmware/](file:///c:/Project/AIoT/digital-twin-physical-ai/firmware/)
- **[protocol_node/](file:///c:/Project/AIoT/digital-twin-physical-ai/firmware/protocol_node/)**: ESP32 code for Modbus/OPC-UA polling and local **Edgie AI** inference.
- **[gateway_node/](file:///c:/Project/AIoT/digital-twin-physical-ai/firmware/gateway_node/)**: ESP32 code for MQTT bridging and **Protocol-Aware Firewall**.

### [simulator/](file:///c:/Project/AIoT/digital-twin-physical-ai/simulator/)
- A multi-protocol industrial sensor simulator (Modbus, BACnet, OPC-UA, EtherNet/IP) with a built-in monitoring dashboard.

### [infrastructure/](file:///c:/Project/AIoT/digital-twin-physical-ai/infrastructure/)
- Deployment and monitoring configurations (Grafana, InfluxDB).

### [research/](file:///c:/Project/AIoT/digital-twin-physical-ai/research/)
- Data visualization and experimental AI models.

### [docs/](file:///c:/Project/AIoT/digital-twin-physical-ai/docs/)
- System architecture, PRDs, and research papers.

### [scripts/](file:///c:/Project/AIoT/digital-twin-physical-ai/scripts/)
- Utility scripts including the `integration_demo.py` and legacy agents.

## 🚀 Quick Start

1. **Setup Project**:
   ```bash
   uv sync
   ```

2. **Start Simulator & Dashboard**:
   ```bash
   uv run .\simulator\main.py
   ```
   *Dashboard available at: [http://localhost:8081/dashboard](http://localhost:8081/dashboard)*

3. **Run Integration Demo**:
   ```bash
   uv run .\scripts\integration_demo.py
   ```

## 🛠️ Key Technologies
- **Edge AI**: TensorFlow Lite for Microcontrollers / ESP-DL.
- **Protocols**: Modbus TCP/RTU, OPC-UA, BACnet/IP, EtherNet/IP (CIP).
- **Backend**: FastAPI, SQLAlchemy, InfluxDB.
- **Cognitive**: LangChain, OpenAI GPT-4o.
- **Security**: Secure Boot V2, Flash Encryption, DPI Firewall.
