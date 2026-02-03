from bacpypes.core import run
from bacpypes.app import Application, BIPSimpleApplication
from bacpypes.object import AnalogValueObject, BinaryValueObject, CalendarObject, ScheduleObject
from bacpypes.local.device import LocalDeviceObject
from bacpypes.primitivedata import Real, Date, Time, Boolean, Null
from bacpypes.basetypes import DateRange, DeviceObjectPropertyReference
from .bacnet_write import handle_write_property
import threading
import time
import logging
import yaml
import os

# Monkeypatch Application instead of BIPSimpleApplication for better dispatch coverage

def do_WritePropertyRequest(self, apdu):
    with open("bacnet_debug.txt", "a") as f:
        try:
            f.write(f"DEBUG: WritePropertyRequest for {apdu.objectIdentifier}\n")
            if not hasattr(self, 'registry') or not self.registry:
                f.write("DEBUG: No registry attached to app\n")
                # Fallback to default
                pass 
            else:
                obj_type, obj_inst = apdu.objectIdentifier
                priority = apdu.priority if apdu.priority else 16
                
                # Use the handle_write_property logic but inline for debug
                sensor = None
                if hasattr(self, 'bacnet_lookup'):
                    if (obj_type, obj_inst) in self.bacnet_lookup:
                        sensor_name = self.bacnet_lookup[(obj_type, obj_inst)]
                        sensor = self.registry.get_sensor(sensor_name)
                    elif obj_inst in self.bacnet_lookup:
                        sensor_name = self.bacnet_lookup[obj_inst]
                        sensor = self.registry.get_sensor(sensor_name)
                elif hasattr(self.registry, 'by_bacnet_instance'):
                    sensor = self.registry.by_bacnet_instance(obj_inst)

                if sensor and obj_type in ("analogValue", "analogInput"):
                    try:
                        value = apdu.propertyValue.cast_out()
                    except:
                        value = apdu.propertyValue.value.cast_out()
                    
                    if isinstance(value, Null):
                        sensor.clear_priority(priority)
                        f.write(f"DEBUG: Cleared priority {priority} for {sensor.name}\n")
                    elif hasattr(value, 'value'):
                        sensor.set_priority(float(value.value), priority)
                        f.write(f"DEBUG: Set {sensor.name} = {value.value} (pri {priority})\n")
                    else:
                        sensor.set_priority(float(value), priority)
                        f.write(f"DEBUG: Set {sensor.name} = {value} (pri {priority})\n")

            from bacpypes.apdu import SimpleAckPDU
            self.response(SimpleAckPDU(context=apdu))
        except Exception as e:
            f.write(f"DEBUG: Error: {e}\n")
            from bacpypes.apdu import ErrorPDU
            self.response(ErrorPDU(context=apdu, errorClass='device', errorCode='operational-problem'))

Application.do_WritePropertyRequest = do_WritePropertyRequest

def run_bacnet(registry, port=47808):
    # Specialized logger for BACpypes
    b_logger = logging.getLogger("bacpypes")
    b_logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler("bacpypes_detailed.log")
    fh.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    b_logger.addHandler(fh)

    device = LocalDeviceObject(
        objectName="SensorSimulator",
        objectIdentifier=1234,
        maxApduLengthAccepted=1024,
        segmentationSupported="segmentedBoth",
        vendorIdentifier=15,
    )

    app = BIPSimpleApplication(device, f"0.0.0.0:{port}")
    app.registry = registry
    app.bacnet_lookup = {}
    app.update_objects = []

    map_path = "config/bacnet_map.yaml"
    if os.path.exists(map_path):
        logging.info(f"Loading BACnet map from {map_path}")
        with open(map_path, "r") as f:
            bacnet_config = yaml.safe_load(f)
        
        # Analog Values
        for instance_id, data in bacnet_config.get("analogValue", {}).items():
            instance_id = int(instance_id)
            sensor_name = data["sensor"]
            sensor = registry.get_sensor(sensor_name)
            if not sensor: continue
            
            obj = AnalogValueObject(
                objectIdentifier=("analogValue", instance_id),
                objectName=sensor.name,
                units="noUnits",
                presentValue=0.0,
                description=f"Simulated {sensor.name}",
                priorityArray=[None] * 16,
                relinquishDefault=0.0,
            )
            app.add_object(obj)
            app.bacnet_lookup[("analogValue", instance_id)] = sensor.name
            app.update_objects.append((obj, sensor))

        # Binary Values
        for instance_id, data in bacnet_config.get("binaryValue", {}).items():
            instance_id = int(instance_id)
            sensor_name = data["sensor"]
            sensor = registry.get_sensor(sensor_name)
            if not sensor: continue
            
            obj = BinaryValueObject(
                objectIdentifier=("binaryValue", instance_id),
                objectName=sensor.name,
                presentValue="inactive",
                description=f"Simulated {sensor.name}",
                priorityArray=[None] * 16,
                relinquishDefault="inactive",
            )
            app.add_object(obj)
            app.bacnet_lookup[("binaryValue", instance_id)] = sensor.name
            app.update_objects.append((obj, sensor))
    else:
        logging.info("BACnet map not found, using default dynamic mapping")
        # Dynamically register sensors
        sorted_sensors = sorted(registry.sensors.values(), key=lambda s: s.name)
        
        for i, sensor in enumerate(sorted_sensors):
            instance_id = i + 1
            obj = AnalogValueObject(
                objectIdentifier=("analogValue", instance_id),
                objectName=sensor.name,
                units="noUnits",
                presentValue=0.0,
                description=f"Simulated {sensor.name}",
                priorityArray=[None] * 16,
                relinquishDefault=0.0,
            )
            app.add_object(obj)
            app.bacnet_lookup[("analogValue", instance_id)] = sensor.name
            app.update_objects.append((obj, sensor))

    def updater():
        while True:
            for obj, sensor in app.update_objects:
                if obj.objectIdentifier[0] == "binaryValue":
                    obj.presentValue = "active" if sensor.value else "inactive"
                    # Convert priority array for binary
                    pa = []
                    for v in sensor.priority_array:
                        if v is None:
                            pa.append(Null())
                        else:
                            pa.append("active" if v else "inactive")
                    obj.priorityArray = pa
                else:
                    obj.presentValue = Real(sensor.value)
                    obj.priorityArray = sensor.priority_array
            time.sleep(1)

    threading.Thread(target=updater, daemon=True).start()
    run()
