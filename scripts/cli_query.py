import os
import sys
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.twin_state import SystemTwin
from backend.core.cognitive_layer import CognitiveLayer

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("cli_query")
logger.setLevel(logging.INFO)

def populate_mock_data(twin: SystemTwin):
    twin.update_environment({"temperature": 23.5, "vibration": 0.02})
    twin.update_or_create_agent("robot_beta", "robot", {"status": "investigating", "battery_level": 78.5})
    twin.process_spatial_event({
        "event_type": "object_detection",
        "zone": "Perimeter_North_Restricted",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detection": {"class": "person", "confidence": 0.98}
    })

def main():
    print("\n=== Digital Twin CLI Query Tool ===")
    
    system_twin = SystemTwin()
    populate_mock_data(system_twin)

    print("Initializing Cognitive Layer...")
    api_url = os.getenv("API_URL", "http://127.0.0.1:8001")
    cognitive = CognitiveLayer(api_url=api_url)

    print("\nSystem Ready. Ask questions about the state.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Query> ").strip()
        if user_input.lower() in ["exit", "quit"]: break
        if user_input:
            summary = system_twin.get_state_summary_for_llm()
            response = cognitive.analyze_system_state(summary, user_input)
            print(f"\nAI: {response}\n")

if __name__ == "__main__":
    main()
