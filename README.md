# LLM-Powered Digital Twin for Physical AI  
### Multi-Agent • Spatial • Interactive

## Overview

This project implements a **research-grade Digital Twin for Physical AI systems** that integrates:

- Static IoT sensors  
- CCTV cameras
- Mobile robots  
- Autonomous drones  
- Smartglasses (AR & Human-in-the-loop)
- Spatial 3D perception  
- LLM-based reasoning and explanation  

The Digital Twin maintains a **live internal representation of the physical world**, models **embodied agents**, and uses a **LangChain-powered cognitive layer** to reason about system behavior, anomalies, and next actions.

The project is developed in **phases**, evolving from telemetry-driven twins to **spatial, multi-agent Physical AI**.

---

## Project Phases

### Phase 1 — State-Centric Digital Twin
- IoT telemetry ingestion (MQTT)
- System Twin + Agent Twins
- Rule-based health evaluation
- Anomaly detection
- LLM reasoning with RAG
- Dashboards and natural language queries

📄 See: `digital_twin_physical_ai_phase_2.md`

---

### Phase 2 — Spatial & Embodied Physical AI *(Current)*

Phase 2 upgrades the Digital Twin with **spatial intelligence and embodiment**.

New capabilities:
- Multi-agent modeling (robots + drones)
- 3D spatial environment representation
- Interactive visualization
- Spatially grounded reasoning

📄 See: `digital_twin_physical_ai_phase_2.md`

---

## System Architecture

![System Diagram](architecture/system_diagram.png)

### Architecture Layers

1. **Physical Layer**
   - IoT sensors (environment, power, vibration)
   - Mobile robots (joints, load, motor health)
   - CCTV cameras (live video feeds)
   - Autonomous drones (pose, battery, perception)
   - Smartglasses (head pose, gaze, voice commands)

2. **Perception & Spatial Layer (Phase 2)**
   - SLAM / pose estimation
   - Gaussian Splatting–based 3D reconstruction
   - Spatial change detection

3. **Data Ingestion Layer**
   - MQTT telemetry
   - Optional ROS2 → MQTT bridge

4. **Digital Twin Core**
   - System Twin (global environment)
   - Agent Twins (robots & drones)
   - Rules engine
   - Anomaly detection

5. **Cognitive Layer**
   - LangChain LLM agent
   - Retrieval-Augmented Generation (RAG)
   - Context-aware reasoning

6. **Interaction Layer**
   - FastAPI
   - Grafana dashboards
   - Natural language interface
   - Interactive 3D viewer

---

## Digital Twin Model

### System Twin
Represents:
- Global environment state
- Infrastructure health
- Spatial zones and history

### Agent Twins (Robots, Drones, & Smartglasses)

Each embodied agent is modeled as an independent **Agent Twin**:

- Pose (position & orientation)
- Velocity
- Battery / power state
- Health & fault indicators
- Active mission
- Perception context

This enables **multi-agent reasoning and coordination**, treating human operators (via Smartglasses) as active agents in the system.

---

## Spatial Digital Twin (Phase 2)

Phase 2 introduces a **spatial representation layer** powered by
**Gaussian Splatting**:

- Drones and robots capture RGB images and pose
- 3D environment is reconstructed and updated
- Spatial changes are detected and converted into structured events
- The Digital Twin reasons over *spatial facts*, not raw pixels

The LLM never consumes images directly — it reasons over **interpretable spatial state**.

---

## Example Questions the System Can Answer

- *Why did drone alpha abort its inspection mission?*
- *Is robot beta safe to continue operation under current load?*
- *Which agent should inspect the detected structural change?*
- *What is the operator looking at right now?*
- *What changed in the environment since yesterday?*

---

## Tech Stack

### Hardware
- IoT MCUs and sensors
- Mobile robots
- Autonomous drones
- Smartglasses (e.g., Vuzix, HoloLens, or ESP32-based DIY)

### Software
- Python
- FastAPI
- MQTT (Mosquitto)
- Optional ROS2 bridge
- InfluxDB (time-series storage)
- Vector database (RAG)

### AI & Visualization
- LangChain
- Retrieval-Augmented Generation (RAG)
- Gaussian Splatting (3D spatial reconstruction)
- Grafana
- Interactive 3D viewer

---

## Getting Started

### Prerequisites
- Python 3.10+
- An MQTT Broker (e.g., Mosquitto) running on `localhost:1883`.
- An OpenAI API Key.

### Installation

1.  **Clone the repository and navigate into it.**

2.  **Create a virtual environment and install dependencies:**
    ```bash
    # Create and activate the virtual environment
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY="your-api-key-here"
    ```

### Running the System

1.  **Initialize the Database:**
    This command creates the `digital_twin.db` file and seeds it with initial data. Run this once.
    ```bash
    python init_db.py
    ```

2.  **Run the Main Server:**
    This starts the FastAPI backend and the web dashboard.
    ```bash
    python run_server.py
    ```
    The API will be available at `http://localhost:8001` and the dashboard at `http://localhost:8001/dashboard/`.

3.  **Start the Sensor Simulation:**
    To generate live data for the dashboard charts, run the mock sensor stream in a separate terminal:
    ```bash
    python backend/agents/mock_sensor_stream.py
    ```

---

## Repository Structure
```
digital-twin-physical-ai/
├── backend/
│ ├── twin/ # System & Agent Twins
│ ├── agents/ # Robot & Drone logic
│ └── cognition/ # LLM reasoning layer
│
├── spatial/
│   ├── gaussian_splatting/
│   ├── pose_sync/
│   └── events/
│       ├── models.py
│       ├── README.md
│       └── cctv_object_detected.json
│
├── visualization/
│ ├── viewer/
│ └── overlays/
│
├── architecture/
│ └── system_diagram.png
│
├── docs/
│ ├── phase1.md
│ ├── phase2.md
│ └── design_decisions.md
│
└── blog/
```

---

## Why This Matters

Most monitoring systems report metrics.

This project demonstrates how to build **thinking physical systems** by:
- Modeling embodied agents
- Grounding AI in real spatial context
- Separating perception, state, and cognition
- Using LLMs for explanation and decision support — not control

It represents a practical step toward **Physical AI and intelligent cyber-physical systems**.

---

## Future Phases

Planned directions:
- Autonomous mission planning
- Multi-agent task allocation
- Simulation ↔ real-world synchronization
- Learned world models
- Closed-loop autonomy experiments

---

## Keywords

Digital Twin · Physical AI · Robotics · Drones · IoT · Gaussian Splatting ·  
LangChain · RAG · Multi-Agent Systems · Spatial Intelligence
