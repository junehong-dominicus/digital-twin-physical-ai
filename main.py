import os
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session

# Import the ORM model from the initialization script
# (Assumes init_db.py is in the same directory)
from init_db import SpatialEvent, Agent, Zone, SystemHealthHistory, Base

app = FastAPI(title="LLM Digital Twin API")

# --- Database Setup ---
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///digital_twin.db")

# Create engine and session factory
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

# Ensure all tables exist (creates system_health_history if missing)
Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Pydantic Models for API Responses ---
class SpatialEventResponse(BaseModel):
    event_id: str
    event_type: str
    source_type: str
    source_id: str
    timestamp: datetime
    zone_id: Optional[str] = None
    object_class: Optional[str] = None
    confidence: Optional[float] = None
    raw_data: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class AgentResponse(BaseModel):
    agent_id: str
    agent_type: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    last_maintenance_date: Optional[datetime] = None
    specs: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class ZoneResponse(BaseModel):
    zone_id: str
    name: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True

@app.get("/")
def root():
    return {"status": "Digital Twin Online"}

@app.get("/events/history", response_model=List[SpatialEventResponse])
def get_spatial_event_history(zone_id: Optional[str] = None, limit: int = 20, db: Session = Depends(get_db)):
    """
    Returns the history of spatial events (detections, zone entries),
    ordered by most recent first. Can be filtered by an optional zone_id.
    """
    query = db.query(SpatialEvent)
    if zone_id:
        query = query.filter(SpatialEvent.zone_id == zone_id)

    events = query.order_by(desc(SpatialEvent.timestamp)).limit(limit).all()
    return events

@app.get("/agents", response_model=List[AgentResponse])
def get_agents(db: Session = Depends(get_db)):
    """
    Returns the list of all registered agents.
    """
    agents = db.query(Agent).all()
    return agents

@app.get("/zones", response_model=List[ZoneResponse])
def get_zones(db: Session = Depends(get_db)):
    """
    Returns the list of all registered zones.
    """
    zones = db.query(Zone).all()
    return zones

@app.get("/sensors")
def get_sensors(db: Session = Depends(get_db)):
    """
    Returns the latest environment sensor data from the system health history.
    """
    latest = db.query(SystemHealthHistory).order_by(desc(SystemHealthHistory.timestamp)).first()
    if latest and latest.environment_snapshot:
        return latest.environment_snapshot
    return {}

@app.get("/sensors/history")
def get_sensor_history(limit: int = 20, db: Session = Depends(get_db)):
    """
    Returns historical environment sensor data for charting.
    """
    history = db.query(SystemHealthHistory).order_by(desc(SystemHealthHistory.timestamp)).limit(limit).all()
    
    data_points = []
    for record in history:
        if record.environment_snapshot:
            point = record.environment_snapshot.copy()
            point["timestamp"] = record.timestamp
            data_points.append(point)
            
    # Return chronological order (oldest to newest) for the chart
    return data_points[::-1]

@app.get("/health/history")
def get_health_history(limit: int = 20, db: Session = Depends(get_db)):
    """
    Returns historical health scores for charting.
    """
    history = db.query(SystemHealthHistory).order_by(desc(SystemHealthHistory.timestamp)).limit(limit).all()
    
    data_points = []
    for record in history:
        data_points.append({
            "timestamp": record.timestamp,
            "health_score": record.health_score,
            "system_status": record.system_status
        })
            
    # Return chronological order (oldest to newest) for the chart
    return data_points[::-1]

# --- Static Files (Dashboard) ---
# Mount the visualization directory to serve the frontend
viewer_path = os.path.join(os.path.dirname(__file__), "visualization", "viewer")
if os.path.exists(viewer_path):
    app.mount("/dashboard", StaticFiles(directory=viewer_path, html=True), name="dashboard")
else:
    print(f"WARNING: Dashboard directory not found at {viewer_path}. UI will not be available.")

@app.get("/ui")
def ui_redirect():
    return RedirectResponse(url="/dashboard/")