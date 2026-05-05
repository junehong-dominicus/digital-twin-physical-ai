import threading
import time
import logging
import cpppo.server.enip
from cpppo.server.enip.get_attribute import proxy_simple

def run_enip(registry, port=44818):
    """
    Simulates an EtherNet/IP (CIP) server.
    Registers are mapped to CIP attributes.
    """
    # Mapping sensors to CIP tags (example: SENSOR_1, SENSOR_2)
    # Using 'REAL' (Float32) for sensor values
    tags = []
    for sensor in registry.sensors.values():
        tags.append(f"{sensor.name.upper()} REAL")

    # Start the EtherNet/IP server
    # Note: cpppo's server.main is quite blocking and designed for CLI, 
    # but we can use its lower level components.
    
    # We will create an attribute proxy and run the server loop
    proxy = proxy_simple()
    
    # Initialize tags in the proxy
    for tag in tags:
        name, _ = tag.split()
        proxy[name] = 0.0

    def updater():
        while True:
            for sensor in registry.sensors.values():
                proxy[sensor.name.upper()] = float(sensor.value)
            time.sleep(1)

    threading.Thread(target=updater, daemon=True).start()
    
    print(f"EtherNet/IP Server starting on port {port}")
    # Run the server (this is blocking)
    cpppo.server.enip.main(host='0.0.0.0', port=port, proxy=proxy)

def start_enip(registry, port=44818):
    threading.Thread(target=run_enip, args=(registry, port), daemon=True).start()
