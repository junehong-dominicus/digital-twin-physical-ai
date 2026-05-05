# 🛰️ Digital Twin Firmware Stack

This directory contains the ESP32 firmware for the Physical AI ecosystem, organized as a multi-node industrial bridge.

## 🧱 Architecture
- **[protocol_node](protocol_node/)**: Industrial Protocol Bridge. Polls Modbus/CAN/BACnet sensors and runs local Edge AI inference (TFLite Micro).
- **[gateway_node](gateway_node/)**: Network Gateway & DPI Firewall. Bridges internal ESP-ONE traffic to MQTT/Cloud and provides security inspection.
- **[shared_components/](shared_components/)**: Shared drivers and protocol definitions (e.g., ESP-ONE) used by both nodes.

## 🛠️ Prerequisites
1. **ESP-IDF v5.x**: Ensure the ESP-IDF environment is installed and sourced.
2. **Hardware**: Two ESP32-S3 or C3 dev kits connected via UART (TX/RX cross-connected).

## 🚀 Build Instructions

### 1. Build the Protocol Node
`ash
cd protocol_node
idf.py set-target esp32s3  # Or your specific target
idf.py build
idf.py -p <PORT> flash
`

### 2. Build the Gateway Node
`ash
cd gateway_node
idf.py set-target esp32s3
idf.py build
idf.py -p <PORT> flash
`

## 📡 ESP-ONE Communication
Both nodes communicate over a high-speed UART link using the proprietary esp_one protocol. 
- **Protocol Node TX**: Pin 17
- **Protocol Node RX**: Pin 16
- **Baud Rate**: 115200
