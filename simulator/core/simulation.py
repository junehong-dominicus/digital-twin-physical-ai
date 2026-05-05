import time
import logging
import threading

def run_simulation_loop(registry, interval=1.0):
    """
    Background loop that updates all sensor values in the registry.
    """
    logging.info(f"Starting simulation loop (interval: {interval}s)")
    
    # Track previous values to log changes for verification
    prev_values = {}
    critical_sensors = ["building_1_motion", "building_1_fire_alarm"]

    while True:
        try:
            registry.update_all()
            
            # Verification: Log specific binary sensors when they change
            for name in critical_sensors:
                sensor = registry.get_sensor(name)
                if sensor:
                    val = sensor.value
                    if prev_values.get(name) != val:
                        logging.info(f"[VERIFY] {name} toggled to {val}")
                        prev_values[name] = val
            
            time.sleep(interval)
        except Exception as e:
            logging.error(f"Error in simulation loop: {e}")
            time.sleep(interval)

def start_simulation(registry, interval=1.0):
    """Starts the simulation loop in a daemon thread."""
    thread = threading.Thread(target=run_simulation_loop, args=(registry, interval), daemon=True)
    thread.start()
    return thread
