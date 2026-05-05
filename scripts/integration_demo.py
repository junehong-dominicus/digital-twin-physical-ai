import sys
import os
import time
import json

# Add project root to sys.path to allow importing backend module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.twin_state import SystemTwin
from backend.core.cognitive_layer import CognitiveLayer

def run_integration_demo():
    print("🚀 STARTING DIGITAL TWIN PHYSICAL AI INTEGRATION DEMO")
    print("------------------------------------------------------")
    
    # 1. Initialize Backend Core
    twin = SystemTwin()
    cognitive = CognitiveLayer()
    
    print("[1/4] Digital Twin Core & Cognitive Layer Initialized.")
    time.sleep(1)

    # 2. Simulate Normal Operation (Telemetry from Gateway)
    print("\n[2/4] Simulating Normal Operation (Telemetry from Gateway Node)")
    normal_telemetry = {
        "temperature": 24.5,
        "vibration": 0.021,
        "edge_ai": {
            "score": 0.05,
            "alert": None
        }
    }
    twin.update_environment(normal_telemetry)
    summary = twin.get_state_summary_for_llm()
    print(f"Current Health Score: {summary['health_score']} ({summary['system_status']})")
    time.sleep(2)

    # 3. Simulate Edge AI Anomaly Detection (Edgie AI Alert)
    print("\n[3/4] !! ALERT: Edgie AI Detected Abnormal Vibration on Protocol Node !!")
    anomaly_telemetry = {
        "temperature": 26.1,
        "vibration": 0.095, # High vibration
        "edge_ai": {
            "score": 0.88,
            "alert": "Critical Bearing Resonance"
        }
    }
    
    # Gateway firewall would have inspected this if it was a command, 
    # but here it's an upstream alert.
    twin.update_environment(anomaly_telemetry)
    summary = twin.get_state_summary_for_llm()
    print(f"Updated Health Score: {summary['health_score']} ({summary['system_status']})")
    time.sleep(1)

    # 4. Trigger Cognitive Reasoning
    print("\n[4/4] Triggering Cognitive Layer Reasoning Agent...")
    print("------------------------------------------------------")
    reasoning = cognitive.analyze_system_state(summary)
    print(reasoning)
    print("------------------------------------------------------")
    print("✅ Integration Demo Completed Successfully.")

if __name__ == "__main__":
    try:
        run_integration_demo()
    except Exception as e:
        print(f"❌ Demo Failed: {e}")
        print("Note: Ensure OPENAI_API_KEY is set for the Cognitive Layer.")
