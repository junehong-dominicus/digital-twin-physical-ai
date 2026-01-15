# LLM-Powered Digital Twin for Physical Systems

## Overview
This project implements a real-time Digital Twin that mirrors
a physical system using IoT sensors, time-series data, and an
LLM-based reasoning agent.

## Architecture
![System Diagram](architecture/system_diagram.png)

## Features
- Live IoT telemetry via MQTT
- Digital Twin state modeling
- Rule-based health evaluation
- Anomaly detection
- LangChain-powered reasoning agent
- Natural language interaction with the twin

## Tech Stack
- ESP32, Sensors
- MQTT (Mosquitto)
- Python, FastAPI
- InfluxDB
- LangChain + Vector DB
- Grafana

## Why This Matters
This project explores how LLMs can act as cognitive layers
on top of physical systems, enabling explainable and
autonomous Digital Twins.
