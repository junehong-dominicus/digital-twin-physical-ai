# Industrial Edge AI: Simulation & Deployment Tools

This directory contains utility scripts for validating the Edge AI integration and deploying TFLite models to the Digital Twin Physical AI firmware.

For a detailed guide on training your own models, see: **[EDGE_AI_WORKFLOW.md](EDGE_AI_WORKFLOW.md)**

## Tools Overview

### 1. Field Data Generator (`field_data_generator.py`)
Generates synthetic industrial telemetry data and injects it directly into the dashboard or AI inference pipeline. This tool is configured to match the 6-dimensional feature vector used by the firmware.

**Usage:**
```bash
uv run field_data_generator.py --broker 127.0.0.1 --node ai-node-01
```
- **Normal Mode**: Generates stable sensor values with minor noise.
- **Anomaly Mode**: Use `--anomaly` to inject spikes and drift for testing detection triggers.

### 2. Model OTA CLI (`model_ota_cli.py`)
The primary tool for deploying new AI models to the edge hardware without requiring a physical serial connection.

**Usage:**
```bash
python model_ota_cli.py --model path/to/model.tflite --target <DEVICE_IP>
```
- **Verification**: Automatically calculates and verifies the CRC16 before and after transmission.
- **Protocol**: Uses the EHIF Model OTA command set (`0xA3` - `0xA5`).

## Workflow for Initial Deployment

If your device logs show a `Model schema mismatch`, follow these steps:

1. **Prepare Model**: Ensure you have a valid `.tflite` model (Version 3 schema).
2. **Deploy**: Run the `model_ota_cli.py` script.
3. **Verify**: Check the device serial logs. You should see:
   - `EDGE_AI_MGR: Model verified. CRC16: 0x...`
   - `EDGE_AI: TFLM Interpreter ready.`
4. **Monitor**: Use the Digital Twin Dashboard to view the real-time anomaly score.

## Dependencies
- Python 3.10+
- `pyserial` (for local serial testing)
- `requests` (if using the REST/EHIF gateway)

## Building Executables
If you modify the source code and need to regenerate the `.exe` files, run:
```bash
python build_exe.py
```
This will use `PyInstaller` to package the scripts into the `dist/` directory.

