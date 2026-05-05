# System Integration & Simulation Roadmap

This document describes the physical architecture and the strategy for simulating industrial environments during development and testing.

## 1. Physical Hardware Architecture

The system uses a dual-node ESP32 architecture for maximum flexibility and performance.

### 1.1 Architecture Flow
`Industrial Devices` <-> `ESP32 Protocol Node` <-> **ESP-ONE** <-> `ESP32 Gateway Node` <-> `MQTT/Cloud`

- **Industrial Protocol Node (ESP32 WROVER)**:
  - Handles time-critical industrial protocols (RS-485, CAN, Ethernet).
  - Performs initial data filtering and normalization.
  - **Edge AI (Edgie AI)**: Implements lightweight on-device AI for anomaly detection and local decision-making.
- **ESP-ONE**:
  - High-speed internal communication bus between the two ESP32 nodes.
- **Gateway Node (ESP32 WROVER)**:
  - Manages cloud connectivity (Wi-Fi, Ethernet, 4G/LTE).
  - Handles MQTT publishing, TLS encryption, and buffering.
  - Implements security firewalls.

## 2. Simulation Strategy

To enable development without constant access to physical PLCs/SCADA systems, a robust simulation environment is utilized.

### 2.1 Industrial Simulators
| Target System | Simulation Software / Method |
| :--- | :--- |
| **PLC / Industrial Hub** | Modbus TCP/RTU, EtherNet/IP, OPC-UA, BACnet, CANopen simulation software. |
| **SCADA** | Virtual SCADA environments mapping to simulated PLCs. |
| **Sensors** | Python-based multi-sensor simulators generating synthetic telemetry. |

### 2.2 Simulator Running Options
- **Option 1: Direct Node Forwarding**: Simulator sends data directly to the ESP32 Protocol Node (testing hardware drivers).
- **Option 2: MQTT Topic Injection**: Simulator publishes data directly to MQTT (testing the Digital Twin core and Dashboards without hardware).

## 3. Integration Testing Roadmap
1. **Module Level**: Validate individual protocol drivers on the Protocol Node.
2. **Bus Level**: Test high-speed data transfer across ESP-ONE.
3. **Network Level**: Verify end-to-end telemetry flow from simulator to Grafana.
4. **Logic Level**: Validate LangChain agent reasoning over simulated anomaly scenarios.
