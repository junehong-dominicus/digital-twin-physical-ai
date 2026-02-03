from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

class AgentTwin:
    """
    Represents the state of a single embodied agent (robot, drone, etc.).
    This aligns with the 'Agent Twins' concept in the project documentation.
    """
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type  # e.g., "robot", "drone", "smartglasses"
        self.status: str = "unknown"  # e.g., "idle", "on_mission", "fault"
        self.last_seen: datetime = datetime.now(timezone.utc)
        
        # Core state attributes from documentation
        self.pose: Dict[str, Any] = {}  # Position and orientation
        self.velocity: Dict[str, Any] = {}
        self.battery_level: Optional[float] = None
        self.active_mission: Optional[str] = None
        
        # Generic container for other telemetry
        self.telemetry: Dict[str, Any] = {}

    def update_telemetry(self, telemetry: dict):
        """Update the agent's state from an incoming telemetry message."""
        self.last_seen = datetime.now(timezone.utc)
        
        # Update core attributes if present
        if "pose" in telemetry:
            self.pose = telemetry["pose"]
        if "velocity" in telemetry:
            self.velocity = telemetry["velocity"]
        if "battery_level" in telemetry:
            self.battery_level = telemetry["battery_level"]
        if "status" in telemetry:
            self.status = telemetry["status"]
        if "mission" in telemetry:
            self.active_mission = telemetry["mission"]
            
        # Store all other telemetry data
        self.telemetry.update(telemetry)

class SystemTwin:
    """
    Represents the holistic state of the entire physical system, including
    the environment and all managed agents. This is the central state object.
    """
    def __init__(self):
        # Global environment state
        self.environment: Dict[str, Any] = {
            "temperature": 0.0,
            "vibration": 0.0,
        }
        self.status: str = "nominal"
        self.health_score: float = 1.0
        
        # Spatial State Management
        self.zones: Dict[str, Dict[str, Any]] = {}
        self.recent_spatial_events: List[Dict[str, Any]] = []

        # Agent Twin Management
        self.agents: Dict[str, AgentTwin] = {}

    def update_environment(self, telemetry: dict):
        """Update global environment state from telemetry (e.g., static IoT sensors)."""
        if "temperature" in telemetry:
            self.environment["temperature"] = telemetry["temperature"]
        if "vibration" in telemetry:
            self.environment["vibration"] = telemetry["vibration"]

    def update_or_create_agent(self, agent_id: str, agent_type: str, telemetry: dict):
        """Updates an existing agent twin or creates a new one."""
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentTwin(agent_id, agent_type)
        
        self.agents[agent_id].update_telemetry(telemetry)

    def process_spatial_event(self, event: dict):
        """
        Process a structured spatial event (e.g., from CCTV perception layer).
        """
        event_type = event.get("event_type")
        zone_id = event.get("zone")
        timestamp = event.get("timestamp", datetime.now(timezone.utc).isoformat())

        # Maintain a rolling log of the last 100 spatial events
        self.recent_spatial_events.append(event)
        if len(self.recent_spatial_events) > 100:
            self.recent_spatial_events.pop(0)

        # Initialize or update the state of the affected zone
        if zone_id:
            if zone_id not in self.zones:
                self.zones[zone_id] = {
                    "last_activity": None,
                    "occupancy_count": 0,
                    "detected_objects": {},
                    "entry_log": []
                }
            
            zone_state = self.zones[zone_id]
            zone_state["last_activity"] = timestamp

            if event_type == "zone_entry":
                zone_state["occupancy_count"] += 1
                zone_state["entry_log"].append({
                    "object_class": event.get("object_class"),
                    "timestamp": timestamp
                })
            
            elif event_type == "object_detection":
                detection = event.get("detection", {})
                obj_class = detection.get("class")
                if obj_class:
                    zone_state["detected_objects"][obj_class] = {
                        "confidence": detection.get("confidence"),
                        "pos_3d": detection.get("estimated_position_3d"),
                        "last_seen": timestamp
                    }

    def calculate_health_score(self) -> float:
        """
        Calculates the aggregate health score (0.0 - 1.0) based on
        environmental factors and agent statuses.
        """
        score = 1.0
        
        # Environment Penalties (Example Thresholds)
        if self.environment.get("temperature", 0) > 45.0:
            score -= 0.2
        if self.environment.get("vibration", 0) > 0.05:
            score -= 0.2
            
        # Agent Penalties
        for agent in self.agents.values():
            if agent.status == "fault":
                score -= 0.3
            elif agent.status == "unknown":
                score -= 0.05
            
            if agent.battery_level is not None and agent.battery_level < 20.0:
                score -= 0.1
                
        self.health_score = max(0.0, min(1.0, score))
        
        # Update semantic status based on score
        if self.health_score >= 0.8:
            self.status = "nominal"
        elif self.health_score >= 0.5:
            self.status = "degraded"
        else:
            self.status = "critical"
            
        return self.health_score

    def get_state_summary_for_llm(self) -> dict:
        """
        Generates a structured summary of the entire system state, suitable for
        the cognitive layer (LLM).
        """
        self.calculate_health_score()
        return {
            "system_status": self.status,
            "health_score": round(self.health_score, 2),
            "environment": self.environment,
            "active_zones": {
                zone: {
                    "last_activity": state["last_activity"],
                    "occupancy": state["occupancy_count"],
                    "detections": list(state["detected_objects"].keys())
                }
                for zone, state in self.zones.items() if state.get("last_activity")
            },
            "agents": [
                {
                    "id": agent.agent_id,
                    "type": agent.agent_type,
                    "status": agent.status,
                    "battery": agent.battery_level,
                    "mission": agent.active_mission,
                    "last_seen": agent.last_seen.isoformat()
                }
                for agent in self.agents.values()
            ]
        }