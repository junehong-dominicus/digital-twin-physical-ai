import time
import random
import math
import os
import sys
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure we can import from the root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from twin_state import SystemTwin
from init_db import SystemHealthHistory

# --- Configuration ---
# Use the same database URL as the main application
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///digital_twin.db")

# --- Database Setup ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def main():
    print(f"Starting Mock Sensor Stream...")
    print(f"Writing to database: {DATABASE_URL}")
    print("Press Ctrl+C to stop.")

    # Initialize the System Twin (in-memory state manager)
    twin = SystemTwin()

    try:
        while True:
            # 1. Simulate Environment Data (Sine wave + Noise)
            # Temperature oscillates between 20 and 25 degrees
            elapsed = time.time()
            temp = 22.5 + 2.5 * math.sin(elapsed / 10.0) + random.uniform(-0.2, 0.2)
            
            # Vibration is low with occasional spikes
            vib = 0.01 + random.uniform(0.0, 0.01)
            if random.random() > 0.95: 
                vib += random.uniform(0.05, 0.15) # Spike

            twin.update_environment({
                "temperature": round(temp, 2),
                "vibration": round(vib, 4)
            })

            # 2. Simulate Agent Status (Mock updates)
            # In a real system, this would come from MQTT agent telemetry
            twin.update_or_create_agent("robot_beta", "robot", {
                "status": "active",
                "battery_level": round(max(0, 100.0 - (elapsed % 300) / 3.0), 1) # Drains over 5 mins
            })
            
            # 3. Calculate Health Score
            twin.calculate_health_score()

            # 4. Persist Snapshot to Database
            session = SessionLocal()
            try:
                snapshot = SystemHealthHistory(
                    timestamp=datetime.now(timezone.utc),
                    health_score=twin.health_score,
                    system_status=twin.status,
                    environment_snapshot=twin.environment,
                    agent_status_snapshot={
                        aid: {"status": a.status, "battery": a.battery_level}
                        for aid, a in twin.agents.items()
                    }
                )
                session.add(snapshot)
                session.commit()
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Updated State: "
                      f"Temp={twin.environment['temperature']}°C, "
                      f"Vib={twin.environment['vibration']}g, "
                      f"Health={twin.health_score:.2f}")
                      
            except Exception as e:
                print(f"Error writing to DB: {e}")
                session.rollback()
            finally:
                session.close()

            # Update frequency
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopping sensor stream.")

if __name__ == "__main__":
    main()