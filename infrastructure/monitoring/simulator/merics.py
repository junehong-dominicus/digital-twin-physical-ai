from prometheus_client import Gauge, Counter

# Sensors
sensor_value = Gauge(
    "sensor_value",
    "Current sensor value",
    ["id", "unit"]
)

sensor_fault = Gauge(
    "sensor_fault_active",
    "Active sensor fault",
    ["id", "type"]
)

# BACnet
bacnet_present_value = Gauge(
    "bacnet_present_value",
    "BACnet PresentValue",
    ["object"]
)

bacnet_active_priority = Gauge(
    "bacnet_active_priority",
    "Active BACnet priority",
    ["object"]
)

bacnet_cov_notifications = Counter(
    "bacnet_cov_notifications_total",
    "BACnet COV notifications",
    ["object"]
)

bacnet_schedule_active = Gauge(
    "bacnet_schedule_active",
    "Schedule active flag",
    ["id"]
)

# Performance
sim_cpu = Gauge(
    "sim_cpu_usage_percent",
    "Simulator CPU usage"
)

sim_tick_latency = Gauge(
    "sim_tick_latency_ms",
    "Main loop latency"
)
