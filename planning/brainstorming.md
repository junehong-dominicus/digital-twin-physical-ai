# Planning & Ideation Workspace

Welcome to the Digital Twin Physical AI planning workspace. This directory contains detailed specifications and roadmaps for the project.

## 📂 Navigation Index

### 1. [Dashboard Requirements](file:///c:/Project/AIoT/digital-twin-physical-ai/planning/01_dashboard_requirements.md)
Specifications for Grafana/Node-RED components, configuration schemas, and UI-to-Topic mapping.

### 2. [Protocol Specifications](file:///c:/Project/AIoT/digital-twin-physical-ai/planning/02_protocol_specifications.md)
Detailed requirements for Modbus (TCP/RTU), BACnet, PROFINET, and other industrial protocols. Includes register mapping and polling logic.

### 3. [Security Architecture](file:///c:/Project/AIoT/digital-twin-physical-ai/planning/03_security_architecture.md)
Hardening requirements for IoT Gateways, including protocol firewalls, secure boot, and hardware encryption.

### 4. [System Integration & Simulation](file:///c:/Project/AIoT/digital-twin-physical-ai/planning/04_system_integration.md)
Hardware flow (ESP32 Protocol Node ↔ Gateway Node), **Edge AI (Edgie AI)** capabilities, and strategies for simulating industrial environments.

---

## 🗒️ Legacy Brainstorming Notes
*The following are raw notes from initial ideation sessions. For current requirements, refer to the documents linked above.*

- **Dashboard Components**: Size, position, color, axis, format, units.
- **Modbus Memory Map**: ranges of registers (function codes, address, multiplier).
- **Physical Protocols**: RS-485, RS-232, CAN, BLE, Wi-Fi, Ethernet.
- **Gateway Requirements**: Multiple protocols, edge computing, cloud integration.
- **Simulation**: Option to forward to ESP32 node or directly to MQTT.
