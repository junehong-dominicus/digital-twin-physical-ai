flowchart TD

%% ===== Physical Layer =====
subgraph PL[Physical Layer]
    S1[IoT Sensors<br/>Temperature, Vibration, Power]
    R1[Mobile Robots<br/>Joints, Load, Motors]
    D1[Autonomous Drones<br/>GPS, IMU, Battery]
end

%% ===== Data Ingestion =====
subgraph DL[Data Ingestion Layer]
    MQTT[MQTT Broker]
    ROS[ROS2 → MQTT Bridge]
end

%% ===== Digital Twin Core =====
subgraph DT[Digital Twin Core]
    ST[System Twin<br/>Environment & Infrastructure]
    AT[Agent Twins<br/>Robots & Drones]
    RULES[Rules Engine]
    ANOM[Anomaly Detection]
end

%% ===== Cognitive Layer =====
subgraph CL[Cognitive Layer]
    LLM[LangChain LLM Agent]
    RAG[Vector DB / RAG]
end

%% ===== Interaction =====
subgraph UI[Interaction & Visualization]
    API[FastAPI]
    DASH[Grafana Dashboards]
    CHAT[Natural Language Interface]
end

%% ===== Flows =====
S1 --> MQTT
R1 --> ROS --> MQTT
D1 --> ROS --> MQTT

MQTT --> ST
MQTT --> AT

ST --> RULES
AT --> RULES
RULES --> ANOM

ST --> LLM
AT --> LLM
RAG --> LLM

LLM --> API
API --> DASH
API --> CHAT
