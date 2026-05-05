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
        
        # Edge AI Insights (Added for Edgie AI)
        self.edge_ai: Dict[str, Any] = {
            "anomaly_score": 0.0,
            "active_alerts": [],
            "last_inference": None
        }

        self.status: str = "nominal"
        self.health_score: float = 1.0
        
        # Spatial State Management
        self.zones: Dict[str, Dict[str, Any]] = {}
        self.recent_spatial_events: List[Dict[str, Any]] = []

        # Agent Twin Management
        self.agents: Dict[str, AgentTwin] = {}

    def update_environment(self, telemetry: dict):
        """Update global environment state and Edge AI insights."""
        # Generic environment update
        for key, value in telemetry.items():
            if key != "edge_ai":
                self.environment[key] = value
        
        # Process Edgie AI data specifically
        if "edge_ai" in telemetry:
            ai_data = telemetry["edge_ai"]
            self.edge_ai["anomaly_score"] = ai_data.get("score", 0.0)
            if ai_data.get("alert"):
                alert = {
                    "reason": ai_data["alert"],
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "severity": "critical" if ai_data.get("score", 0) > 0.8 else "warning"
                }
                self.edge_ai["active_alerts"].append(alert)
                # Keep only last 5 alerts
                if len(self.edge_ai["active_alerts"]) > 5:
                    self.edge_ai["active_alerts"].pop(0)

    def calculate_health_score(self) -> float:
        """
        Calculates the aggregate health score (0.0 - 1.0).
        Prioritizes Edge AI anomaly scores for real-time fault detection.
        """
        score = 1.0
        
        # 1. Edge AI Penalty (Weighted Heavily)
        # Anomaly score of 1.0 results in 0.5 health reduction
        score -= (self.edge_ai["anomaly_score"] * 0.5)
        
        # 2. Environment Penalties (Baseline)
        if self.environment.get("temperature", 0) > 45.0:
            score -= 0.1
        if self.environment.get("vibration", 0) > 0.05:
            score -= 0.1
            
        # 3. Agent Penalties
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
        Generates a structured summary for the LLM, including Edge AI insights.
        """
        self.calculate_health_score()
        return {
            "system_status": self.status,
            "health_score": round(self.health_score, 2),
            "edge_ai_insights": self.edge_ai,
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