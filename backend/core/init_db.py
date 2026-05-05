import os
import sys
import uuid
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, String, Float, Boolean, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.types import JSON

# --- ORM Definitions matching schema.sql ---

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'agents'
    agent_id = Column(String(50), primary_key=True)
    agent_type = Column(String(20), nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_maintenance_date = Column(DateTime(timezone=True))
    specs = Column(JSON)

class Zone(Base):
    __tablename__ = 'zones'
    zone_id = Column(String(50), primary_key=True)
    name = Column(String(100))
    description = Column(Text)
    coordinates_3d = Column(JSON)
    is_restricted = Column(Boolean, default=False)

class SpatialEvent(Base):
    __tablename__ = 'spatial_events'
    event_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(50), nullable=False)
    source_type = Column(String(20), nullable=False)
    source_id = Column(String(50), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    zone_id = Column(String(50), ForeignKey('zones.zone_id'))
    object_class = Column(String(50))
    confidence = Column(Float)
    raw_data = Column(JSON)

class SystemHealthHistory(Base):
    __tablename__ = 'system_health_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    health_score = Column(Float, nullable=False)
    system_status = Column(String(20), nullable=False)
    environment_snapshot = Column(JSON)
    agent_status_snapshot = Column(JSON)

class AgentMission(Base):
    __tablename__ = 'agent_missions'
    mission_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(50), ForeignKey('agents.agent_id'))
    status = Column(String(20), nullable=False)
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    description = Column(Text)
    priority = Column(Integer, default=1)

# --- Initialization Script ---

def init_db_and_seed():
    # Defaults to a local SQLite file, but compatible with PostgreSQL connection strings
    db_url = os.getenv("DATABASE_URL", "sqlite:///digital_twin.db")
    engine = create_engine(db_url)
    
    print(f"Initializing database at {db_url}...")
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Seed Agents (matching cli_query.py mock data)
    print("Seeding Agents...")
    robot = Agent(
        agent_id="robot_beta",
        agent_type="robot",
        name="Robot Beta (Spot)",
        specs={"max_load": 15.0, "battery_capacity": 6000}
    )
    drone = Agent(
        agent_id="drone_alpha",
        agent_type="drone",
        name="Drone Alpha (DJI)",
        specs={"max_flight_time": 30, "camera_resolution": "4k"}
    )
    
    # Upsert logic (simple check for existence)
    if not session.query(Agent).filter_by(agent_id="robot_beta").first():
        session.add(robot)
    if not session.query(Agent).filter_by(agent_id="drone_alpha").first():
        session.add(drone)

    # 2. Seed Zones
    print("Seeding Zones...")
    zone_id = "Perimeter_North_Restricted"
    if not session.query(Zone).filter_by(zone_id=zone_id).first():
        zone = Zone(
            zone_id=zone_id,
            name="North Perimeter Restricted Area",
            description="High security zone near the north fence.",
            is_restricted=True,
            coordinates_3d={"polygon": [[0, 80], [20, 80], [20, 100], [0, 100]]}
        )
        session.add(zone)

    # 3. Seed Spatial Event (Mock detection from cli_query.py)
    print("Seeding Spatial Events...")
    event = SpatialEvent(
        event_type="object_detection",
        source_type="cctv",
        source_id="cctv_cam_04",
        timestamp=datetime.now(timezone.utc),
        zone_id=zone_id,
        object_class="person",
        confidence=0.98,
        raw_data={
            "detection": {
                "class": "person",
                "confidence": 0.98,
                "estimated_position_3d": {"x": 15.0, "y": 88.0, "z": 1.6}
            }
        }
    )
    session.add(event)

    # 4. Seed Missions
    print("Seeding Missions...")
    mission_robot = AgentMission(
        agent_id="robot_beta",
        status="active",
        start_time=datetime.now(timezone.utc),
        description="perimeter_check",
        priority=2
    )
    session.add(mission_robot)

    # 5. Seed System Health Snapshot
    print("Seeding Health History...")
    # Based on cli_query.py: Temp 23.5, Vib 0.02, Robot Batt 78.5, Drone Batt 92.0 -> Score 1.0
    health_snapshot = SystemHealthHistory(
        health_score=1.0,
        system_status="nominal",
        environment_snapshot={"temperature": 23.5, "vibration": 0.02},
        agent_status_snapshot={
            "robot_beta": {"status": "investigating", "battery": 78.5},
            "drone_alpha": {"status": "idle", "battery": 92.0}
        }
    )
    session.add(health_snapshot)

    session.commit()
    print("Database initialized and seeded successfully.")
    session.close()

if __name__ == "__main__":
    init_db_and_seed()