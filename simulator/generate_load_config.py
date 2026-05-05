import yaml
import os

# Configuration
OUTPUT_DIR = "config"

def main():
    sensors = []
    input_registers = {}
    discrete_inputs = {}
    holding_registers = {}
    mqtt_topics = {}
    bacnet_objects = {}

    # Modbus starting addresses
    # 30001+ for Input Registers (Analog Inputs)
    # 10001+ for Discrete Inputs (Binary Inputs)
    # 40001+ for Holding Registers (Writable Setpoints)
    ir_counter = 30001
    di_counter = 10001
    hr_counter = 40001
    av_counter = 1
    bv_counter = 1

    # Load templates from config file
    presets_path = os.path.join(OUTPUT_DIR, "generator_presets.yaml")
    if not os.path.exists(presets_path):
        print(f"Error: {presets_path} not found.")
        return

    with open(presets_path, "r") as f:
        presets = yaml.safe_load(f)

    num_buildings = presets.get("settings", {}).get("num_buildings", 50)
    templates = presets.get("templates", [])

    print(f"Generating configuration for {num_buildings} buildings...")

    for i in range(1, num_buildings + 1):
        building_id = f"building_{i}"
        
        for t in templates:
            sensor_name = f"{building_id}_{t['suffix']}"
            
            # 1. Sensor Definition
            sensor_def = {
                "name": sensor_name,
                "unit": t["unit"],
                "base": float(t["base"]),
                "min": float(t["min"]),
                "max": float(t["max"]),
                "writable": t["writable"],
                "simulation_type": t["type"]
            }
            
            # Copy optional simulation parameters
            for k in ["noise", "spike_chance", "spike_multiplier", "period", "pulse_width"]:
                if k in t:
                    sensor_def[k] = t[k]
            sensors.append(sensor_def)

            # 2. Modbus Mapping
            if t["modbus"] == "ir":
                input_registers[ir_counter] = {"sensor": sensor_name, "scale": t.get("scale", 1)}
                ir_counter += 1
            elif t["modbus"] == "di":
                discrete_inputs[di_counter] = {"sensor": sensor_name}
                di_counter += 1
            elif t["modbus"] == "hr":
                holding_registers[hr_counter] = {"sensor": sensor_name, "scale": t.get("scale", 1), "writable": True}
                hr_counter += 1

            # 3. MQTT Mapping
            mqtt_topics[sensor_name] = f"campus/{building_id}/{t['suffix']}"

            # 4. BACnet Mapping
            if t["unit"] == "bool":
                obj_type = "binaryValue"
                instance = bv_counter
                bv_counter += 1
            else:
                obj_type = "analogValue"
                instance = av_counter
                av_counter += 1
            
            if obj_type not in bacnet_objects:
                bacnet_objects[obj_type] = {}
            bacnet_objects[obj_type][instance] = {"sensor": sensor_name}

    # Prepare final data structures
    sensors_data = {"sensors": sensors}
    
    modbus_data = {
        "holding_registers": holding_registers,
        "input_registers": input_registers,
        "discrete_inputs": discrete_inputs
    }
    
    mqtt_data = {"topics": mqtt_topics}

    # Write to files
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, "sensors.yaml"), "w") as f:
        yaml.dump(sensors_data, f, sort_keys=False)
    
    with open(os.path.join(OUTPUT_DIR, "modbus_map.yaml"), "w") as f:
        yaml.dump(modbus_data, f, sort_keys=False)

    with open(os.path.join(OUTPUT_DIR, "mqtt_map.yaml"), "w") as f:
        yaml.dump(mqtt_data, f, sort_keys=False)

    with open(os.path.join(OUTPUT_DIR, "bacnet_map.yaml"), "w") as f:
        yaml.dump(bacnet_objects, f, sort_keys=False)

    print(f"Done! Generated {len(sensors)} sensors across {num_buildings} buildings.")
    print(f"Files saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()