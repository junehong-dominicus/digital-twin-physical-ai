-- Database Schema for Digital Twin Physical AI
-- Compatible with PostgreSQL
--
-- This schema aligns with the SystemTwin and AgentTwin classes defined in backend/twin/twin_state.py
-- and the spatial events defined in spatial/events/models.py.

-- 1. Agents Registry
-- Stores static metadata about physical agents.
-- Real-time telemetry (pose, battery) is stored in InfluxDB, but the entity exists here.
CREATE TABLE agents (
    agent_id VARCHAR(50) PRIMARY KEY,
    agent_type VARCHAR(20) NOT NULL, -- 'robot', 'drone', 'smartglasses'
    name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_maintenance_date TIMESTAMP WITH TIME ZONE,
    specs JSONB -- Store hardware specs: {"max_load": 50, "battery_capacity": 5000}
);

-- 2. Spatial Zones
-- Defines the semantic zones in the physical environment referenced by SystemTwin.
CREATE TABLE zones (
    zone_id VARCHAR(50) PRIMARY KEY, -- e.g., 'Perimeter_North_Restricted'
    name VARCHAR(100),
    description TEXT,
    coordinates_3d JSONB, -- Defines the bounding box or polygon points
    is_restricted BOOLEAN DEFAULT FALSE
);

-- 3. Spatial Events Log
-- Persists structured events from the Perception Layer.
-- Maps directly to spatial/events/models.py JSON structure.
CREATE TABLE spatial_events (
    event_id UUID PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- 'object_detection', 'zone_entry'
    source_type VARCHAR(20) NOT NULL, -- 'cctv', 'drone', 'robot'
    source_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    zone_id VARCHAR(50) REFERENCES zones(zone_id),
    
    -- Extracted high-level fields for fast querying
    object_class VARCHAR(50), -- e.g., 'person', 'vehicle'
    confidence FLOAT,
    
    -- Full event payload (including 3D position, bounding boxes)
    raw_data JSONB
);

-- Indexes for common query patterns (e.g., "Show me all detections in Zone A today")
CREATE INDEX idx_spatial_events_ts ON spatial_events(timestamp);
CREATE INDEX idx_spatial_events_zone ON spatial_events(zone_id);
CREATE INDEX idx_spatial_events_class ON spatial_events(object_class);

-- 4. System Health Snapshots
-- Records the aggregate health score calculated by SystemTwin.calculate_health_score()
CREATE TABLE system_health_history (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    health_score FLOAT NOT NULL,
    system_status VARCHAR(20) NOT NULL, -- 'nominal', 'degraded', 'critical'
    
    -- Snapshot of environmental metrics at this time
    environment_snapshot JSONB, -- {"temperature": 23.5, "vibration": 0.02}
    
    -- Snapshot of agent statuses to correlate with health drops
    agent_status_snapshot JSONB -- {"robot_beta": "fault", "drone_alpha": "idle"}
);

-- 5. Agent Missions
-- Tracks high-level tasks assigned to agents
CREATE TABLE agent_missions (
    mission_id UUID PRIMARY KEY,
    agent_id VARCHAR(50) REFERENCES agents(agent_id),
    status VARCHAR(20) NOT NULL, -- 'pending', 'active', 'completed', 'aborted'
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    description TEXT,
    priority INT DEFAULT 1
);