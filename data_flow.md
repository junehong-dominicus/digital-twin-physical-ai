# Data Flow

1. **Sensors (ESP32)** -> MQTT Broker (Topic: `sensors/telemetry`)
2. **MQTT Listener** -> Ingests data -> Updates **Twin State**
3. **Twin State** -> Runs **Rules** & **Anomaly Detection**
4. **Twin State** -> Persisted to **InfluxDB**
5. **User Query** -> **LangChain Agent**
6. **LangChain Agent** -> Retrieves **Twin State** + **Vector DB (RAG)**
7. **LangChain Agent** -> Returns Answer