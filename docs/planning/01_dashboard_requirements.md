# Dashboard Requirements & Specifications

This document defines the requirements for the Digital Twin visualization layer, including component types, configuration schemas, and data mapping logic.

## 1. Supported Platforms
- **Grafana Dashboard**: Primary visualization for time-series data (InfluxDB).
- **Node-RED Dashboard**: Used for rapid prototyping and local control interfaces.
- **ThingsBoard Dashboard**: Enterprise-grade IoT device management and visualization.

## 2. Key Dashboard Component Types

| Component Type | Description | Use Cases |
| :--- | :--- | :--- |
| **Charts** | Bar, line, pie, and area charts. | Trend analysis, historical data, real-time telemetry. |
| **Tables** | Structured, detailed data presentation. | Device lists, event logs, maintenance records. |
| **KPI Cards** | High-level metrics at a glance. | Health score, total uptime, current efficiency. |
| **Gauges** | Speedometer-style indicators. | Temperature, pressure, RPM, battery level. |
| **Interactive Widgets** | Selectors, sliders, date pickers. | Filtering data, adjusting setpoints, user input. |
| **Edge AI Insights** | Confidence scores, anomaly heatmaps, inference status. | Real-time Edge AI diagnostics and local alerts. |
| **Layout Elements** | Containers, tabs, section dividers. | Organizing dashboard structure and navigation. |

## 3. Configuration Parameters
Each dashboard component requires a set of parameters for consistent rendering and behavior:

- **Identity**: ID, Title, Description, Icon, Label.
- **Geometry**: Size (width/height), Position (x/y).
- **Visuals**: Color palette, Axis config, Legend config.
- **Data Formatting**: Units, Number of decimals, Threshold config (min/max/critical).
- **Connectivity**: Data source config, Refresh rate.

## 4. Topic-to-Dashboard Mapping (JSON Configuration)
The system uses a JSON-based mapping configuration to link MQTT topics with specific dashboard components.

### 4.1 Topic to Dashboard (Inbound)
- **Type**: gauge, chart, table, kpi, interactive, layout.
- **Component ID/Name**: Reference to the dashboard element.
- **Dashboard Name**: Target dashboard instance.
- **Parameters**: Component-specific settings.

### 4.2 Dashboard to Topic (Outbound/Control)
- **Modbus mapping**: Link dashboard inputs (e.g., setpoints) to specific Modbus registers.
- **Command structure**: Define the MQTT payload structure for actuation.

## 5. Dashboard Configuration Editor
A dedicated editor tool is required to manage these configurations without manual JSON editing.
- UI for dragging and dropping components.
- Property panel for editing the parameters listed in Section 3.
- Live preview functionality.
