# Data Flow

1. **Sensors (IoT MCUs)** -> MQTT Broker
2. **CCTV Cameras** -> **Perception Layer** -> **Structured JSON Events**
3. **MQTT Listener** -> Ingests Telemetry & Events -> Updates **Twin State**
4. **Twin State** -> Runs **Rules** & **Anomaly Detection**
5. **Twin State** -> Persisted to **InfluxDB**
6. **User Query** -> **LangChain Agent**
7. **LangChain Agent** -> Retrieves **Twin State** + **Vector DB (RAG)**
8. **LangChain Agent** -> Returns Answer