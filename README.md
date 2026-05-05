# Digital Twin Physical AI

This repository contains a professional, industrial-grade Digital Twin platform integrated with Edge AI (Edgie AI) and a Cognitive Layer for autonomous reasoning.

## 📁 Repository Structure

### [backend/](file:///c:/Project/AIoT/digital-twin-physical-ai/backend/)
- **[core/](file:///c:/Project/AIoT/digital-twin-physical-ai/backend/core/)**: The brain of the twin. Contains `twin_state.py` (Central State) and `cognitive_layer.py` (LLM Reasoning).
- **[api/](file:///c:/Project/AIoT/digital-twin-physical-ai/backend/api/)**: FastAPI application for serving telemetry and dashboard data.

### [firmware/](file:///c:/Project/AIoT/digital-twin-physical-ai/firmware/)
- **[protocol_node/](file:///c:/Project/AIoT/digital-twin-physical-ai/firmware/protocol_node/)**: ESP32 code for Modbus/OPC-UA polling and local **Edgie AI** inference.
- **[gateway_node/](file:///c:/Project/AIoT/digital-twin-physical-ai/firmware/gateway_node/)**: ESP32 code for MQTT bridging and **Protocol-Aware Firewall**.

### [simulator/](file:///c:/Project/AIoT/digital-twin-physical-ai/simulator/)
- A multi-protocol industrial sensor simulator (Modbus, BACnet, OPC-UA, EtherNet/IP) used for end-to-end testing without physical hardware.

### [planning/](file:///c:/Project/AIoT/digital-twin-physical-ai/planning/)
- Technical specifications, security architectures, and system integration plans.

### [docs/](file:///c:/Project/AIoT/digital-twin-physical-ai/docs/)
- System architecture diagrams, data flow models, and PRDs.

### [scripts/](file:///c:/Project/AIoT/digital-twin-physical-ai/scripts/)
- Utility scripts including the `integration_demo.py`.

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Integration Demo**:
   ```bash
   python scripts/integration_demo.py
   ```

3. **Start Simulator**:
   ```bash
   python simulator/main.py
   ```

## 🛠️ Key Technologies
- **Edge AI**: TensorFlow Lite for Microcontrollers / ESP-DL.
- **Protocols**: Modbus TCP/RTU, OPC-UA, BACnet/IP, EtherNet/IP (CIP).
- **Backend**: FastAPI, SQLAlchemy, InfluxDB.
- **Cognitive**: LangChain, OpenAI GPT-4o.
- **Security**: Secure Boot V2, Flash Encryption, DPI Firewall.
