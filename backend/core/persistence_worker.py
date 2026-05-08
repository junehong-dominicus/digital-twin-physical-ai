import os
import sys
import json
import time
import threading
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from backend.core.twin_state import SystemTwin
from backend.core.init_db import SystemHealthHistory, Base

class PersistenceWorker:
    """
    Background worker that bridges MQTT telemetry to the SQL database.
    It maintains an in-memory SystemTwin state and periodically persists snapshots.
    """
    def __init__(self, broker="localhost", port=1883, db_url=None):
        self.broker = broker
        self.port = port
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///digital_twin.db")
        
        # Initialize Digital Twin State
        self.twin = SystemTwin()
        
        # Database setup
        self.engine = create_engine(self.db_url, connect_args={"check_same_thread": False} if "sqlite" in self.db_url else {})
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # MQTT Client
        try:
            # Try Paho-MQTT 2.0 API first
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        except AttributeError:
            # Fallback to Paho-MQTT 1.x
            self.client = mqtt.Client()
            
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        self.running = False
        self.last_persist_time = 0
        self.persist_interval = 5  # Persist to DB every 5 seconds

    def on_connect(self, client, userdata, flags, rc, properties=None):
        print(f"Persistence Worker connected to MQTT broker with result code {rc}")
        # Subscribe to all campus telemetry
        client.subscribe("campus/#")
        # Also subscribe to agent telemetry if any
        client.subscribe("agents/#")

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            value = float(payload) if payload.replace('.', '', 1).isdigit() else payload
            
            # Extract sensor name from topic (e.g., campus/building_1/temperature -> building_1_temperature)
            parts = topic.split('/')
            if len(parts) >= 3:
                sensor_name = f"{parts[1]}_{parts[2]}"
                
                # Update Twin State
                # For this demo, we treat all campus topics as environment updates
                self.twin.update_environment({parts[2]: value})
                
                # Store the specific sensor in a temporary environment buffer
                if "full_env" not in self.twin.environment:
                    self.twin.environment["full_env"] = {}
                self.twin.environment["full_env"][sensor_name] = value

        except Exception as e:
            print(f"Error processing MQTT message: {e}")

    def persist_snapshot(self):
        """Saves a snapshot of the current twin state to the database."""
        session = self.SessionLocal()
        try:
            # Calculate aggregate health
            health_score = self.twin.calculate_health_score()
            
            # Prepare snapshots
            env_snapshot = self.twin.environment.get("full_env", {})
            agent_snapshot = {
                id: {"status": a.status, "battery": a.battery_level}
                for id, a in self.twin.agents.items()
            }
            
            # Create DB record
            record = SystemHealthHistory(
                health_score=health_score,
                system_status=self.twin.status,
                environment_snapshot=env_snapshot,
                agent_status_snapshot=agent_snapshot,
                timestamp=datetime.now(timezone.utc)
            )
            
            session.add(record)
            session.commit()
            # print(f"Persisted state snapshot to DB (Health: {health_score:.2f})")
        except Exception as e:
            print(f"Failed to persist snapshot: {e}")
            session.rollback()
        finally:
            session.close()

    def run(self):
        self.running = True
        try:
            self.client.connect(self.broker, self.port, 60)
            # Start MQTT loop in a separate thread
            self.client.loop_start()
            print(f"Persistence Worker started. Monitoring {self.broker}:{self.port}...")
        except Exception as e:
            print(f"⚠️ Persistence Worker: Could not connect to MQTT broker ({e}). Retrying in background...")
        
        try:
            while self.running:
                current_time = time.time()
                if current_time - self.last_persist_time >= self.persist_interval:
                    self.persist_snapshot()
                    self.last_persist_time = current_time
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.running = False
        self.client.loop_stop()
        self.client.disconnect()
        print("Persistence Worker stopped.")

if __name__ == "__main__":
    worker = PersistenceWorker()
    worker.run()
