import os
import sys
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load environment variables (ensure OPENAI_API_KEY is set)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("cli_query")
logger.setLevel(logging.INFO)

try:
    from twin_state import SystemTwin
    from langchain_agent import DigitalTwinAgent
except ImportError:
    # Allow running if dependencies are in the current directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from twin_state import SystemTwin
    from langchain_agent import DigitalTwinAgent

def populate_mock_data(twin: SystemTwin):
    """Populates the SystemTwin with a rich mock scenario."""
    logger.info("Populating Digital Twin with mock data...")

    # 1. Environment Data (Static Sensors)
    twin.update_environment({
        "temperature": 23.5,
        "vibration": 0.02
    })

    # 2. Agent: Mobile Robot (Responding to an event)
    twin.update_or_create_agent("robot_beta", "robot", {
        "status": "investigating",
        "battery_level": 78.5,
        "pose": {"x": 12.5, "y": 45.2, "theta": 1.57},
        "mission": "perimeter_check"
    })

    # 3. Agent: Drone (Docked)
    twin.update_or_create_agent("drone_alpha", "drone", {
        "status": "idle",
        "battery_level": 92.0,
        "mission": "docked"
    })

    # 4. Spatial Event: Person detected in restricted zone
    twin.process_spatial_event({
        "event_type": "object_detection",
        "zone": "Perimeter_North_Restricted",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "detection": {
            "class": "person",
            "confidence": 0.98,
            "estimated_position_3d": {"x": 15.0, "y": 88.0, "z": 1.6}
        }
    })

    logger.info("Mock data loaded successfully.")

def main():
    print("\n=== Digital Twin CLI Query Tool ===")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found. Please set it in your .env file.")
        return

    # Initialize System and Agent
    system_twin = SystemTwin()
    populate_mock_data(system_twin)

    # Calculate and display initial health score
    score = system_twin.calculate_health_score()
    print(f"System Health Score: {score:.2f} (Status: {system_twin.status})")
    
    print("Initializing AI Agent...")
    api_url = os.getenv("API_URL", "http://127.0.0.1:8001")
    agent = DigitalTwinAgent(api_url=api_url)

    print("\nSystem Ready. Ask questions about the state (e.g., 'Why is the robot investigating?').")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Query> ").strip()
        if user_input.lower() in ["exit", "quit"]:
            break
        if user_input:
            response = agent.ask(user_input, system_twin)
            print(f"\nAI: {response}\n")

if __name__ == "__main__":
    main()