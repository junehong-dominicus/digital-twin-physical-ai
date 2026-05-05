# Industrial Protocol Specifications

This document outlines the technical requirements and configuration for industrial communication protocols supported by the Digital Twin Physical AI platform.

## 1. Supported Protocols
The system is designed to support a wide range of industrial communication standards:
- **Modbus TCP / RTU**: Primary legacy protocol support.
- **CIP EtherNet/IP**: Rockwell Automation / Allen-Bradley integration.
- **OPC-UA**: Secure, platform-independent industrial communication.
- **BACnet/IP**: Building automation and control networks.
- **PROFINET / PROFIBUS**: Siemens and European industrial standards.
- **CANopen**: Motion control and embedded system communication.

## 2. Modbus Specification
The implementation focus is currently on Modbus (TCP/RTU) with the following configuration requirements.

### 2.1 Memory Map Configuration
For each device, a memory map must be defined:
- **Device Type**: Modbus TCP or Modbus RTU.
- **Slave ID**: Unique identifier for the device on the bus.
- **Register Ranges**:
  - **Function Codes**: (01: Coil, 02: Discrete Input, 03: Holding Register, 04: Input Register).
  - **Address**: Starting register address.
  - **Data Type**: Int16, Uint16, Float32, etc.
  - **Scaling**: Multiplier and Offset for raw value conversion.
  - **Access**: `is_writable`, `is_readable` flags.

### 2.2 Network & Polling Logic
- **Polling Rate**: Configurable interval for data collection.
- **Retries**: Number of attempts before marking a node as offline.
- **Timeout**: Wait time for responses.
- **Mapping**: Association between registers and MQTT topics.

## 3. Protocol Transition Logic (ESP-ONE)
Data flows from specific industrial protocols through the ESP32 Protocol Node, then via **ESP-ONE** (internal bus) to the ESP32 Gateway Node for cloud publishing.

### 3.1 Topic Mapping
Each industrial data point is mapped to a standard MQTT topic structure:
`[site]/[area]/[device]/[protocol]/[point_name]`

### 3.2 Edge AI Integration
Normalized protocol data is streamed to the **Edge AI (Edgie AI)** engine on the ESP32 WROVER for real-time inference before being published to the gateway.

## 4. Protocol Configuration Editor
An interface to manage these complex mappings is essential to avoid manual errors.
- Template system for common industrial devices (PLCs, VFDs).
- Register range validator.
- Real-time polling diagnostic tool.
