Dashboard Component Types:
Key Dashboard Component Types
- Charts: Visual representations such as bar, line, and pie charts used for trend analysis and real-time data insights.
- Tables: Structured, detailed data presentation for rows of information.
- KPI Cards/Metrics: Key Performance Indicators that display crucial, high-level business numbers at a glance.
- Gauges/Indicators: Speedometer-style tools, often showing status against a target, such as fuel, temperature, or performance levels.
- Interactive Widgets: Selectors, sliders, and date range pickers that enable users to filter data dynamically.
- Layout Elements: Containers, Tabs, and Section dividers that organize components within a structured grid.

Dashboard :
- Grafana Dashboard
- Node-RED Dashboard
- ThingsBoard Dashboard
- dashboard configuration componenets : size position color chart type range min max unit title description icon label color axis config format units, number of decimals, legend config, threshold config, data source config, refresh rate
- editor for dashboard components configuration

1. Modbus
1) Modbus memory map to topic
 - device (Modbus TCP / Modbus RTU)
 - slave id
 - ranges of registers (function codes, register address, data type, range, multiplier, offset, is_writable, is_readable)
 - polling rate
 - retries
 - timeout
 - mapping
 - editor for this
   - 

2) topic and dashboard mapping (Json config)
  - topic to dashboard
    - type: gauge, chart, table, kpi, interactive, layout
    - component name
    - dashboard name
    - parameters
  - dashboard to topic
    - Modbus memory map config (ranges, polling rate, retries, timeout)
    - mapping
 - editor for this

2. CIP EtherNet/IP

3. OPC-UA

4. BACnet

5. PROFINET

6. PROFIBUS

7. CANopen  

Security Features in my Gateways:
- Configurable one-way traffic (industrial protocol -> cloud)
- Protocol-Aware Firewalls: Some gateways serve as dedicated "Protocol Firewalls" that can understand specific industrial protocols rather than just blocking IP addresses.
- Secure Boot & Integrity Management: Ensuring that only trusted software runs on the gateway, protecting against malware.
- Independent Security Chips: Advanced IoT gateways may feature dedicated hardware security modules for handling encryption key management

Industrial IoT Gateway Requirements: 
- Modbus TCP / RTU
- EtherNet/IP 
- OPC-UA
- BACnet/IP 
- PROFINET
- PROFIBUS
- CANopen
- Protocol-Aware Firewalls
- Secure Boot & Integrity Management
- Independent Security Chips
- Multiple Industrial Protocols Support
- Data Processing and Edge Computing Capabilities
- Cloud Integration and Connectivity
- Device Management and Monitoring

    
industrial protocols Modbus TCP / RTU, EtherNet/IP, OPC-UA, BACnet/IP, PROFINET, PROFIBUS, CANopen <-> ESP32 protocol node <-> ESP-ONE <-> ESP32 gateway node <-> TCP/IP (Ethernet/Wifi/4G/5G/LTE) <-> MQTT <-> MQTT Broker <-> InfluxDB <-> dashboard mapping config -> Grafana dashboard

Simulation:
- PLC: Modbus TCP / RTU, EtherNet/IP, OPC-UA, BACnet/IP, PROFINET, PROFIBUS, CANopen simulation software
- SCADA: Modbus TCP / RTU, EtherNet/IP, OPC-UA, BACnet/IP, PROFINET, PROFIBUS, CANopen simulation software
simulator running options:
option 1: forward to ESP32 protocol node
option 2: forward to MQTT Topic
