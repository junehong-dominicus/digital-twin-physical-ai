from bacpypes.core import run
from bacpypes.app import Application, BIPSimpleApplication
from bacpypes.object import AnalogValueObject, CalendarObject, ScheduleObject
from bacpypes.local.device import LocalDeviceObject
from bacpypes.primitivedata import Real, Date, Time, Boolean, Null
from bacpypes.basetypes import DateRange, DeviceObjectPropertyReference
from .bacnet_write import handle_write_property
import threading
import time
import logging

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

def run_bacnet(registry):
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

    app = BIPSimpleApplication(device, "127.0.0.1:47808")
    app.registry = registry

    ai_temp = AnalogValueObject(
        objectIdentifier=("analogValue", 1),
        objectName="Temperature",
        units="degreesCelsius",
        presentValue=0.0,
        description="Simulated Temperature",
        priorityArray=[None] * 16,
        relinquishDefault=0.0,
    )

    ai_hum = AnalogValueObject(
        objectIdentifier=("analogValue", 2),
        objectName="Humidity",
        units="percent",
        presentValue=0.0,
        priorityArray=[None] * 16,
        relinquishDefault=0.0,
    )

    ai_pres = AnalogValueObject(
        objectIdentifier=("analogValue", 3),
        objectName="Pressure",
        units="pascals",
        presentValue=0.0,
        priorityArray=[None] * 16,
        relinquishDefault=0.0,
    )

    # Calendar Object
    calendar = CalendarObject(
        objectIdentifier=("calendar", 1),
        objectName="Holidays",
        dateList=[]
    )

    # Schedule Object
    schedule = ScheduleObject(
        objectIdentifier=("schedule", 1),
        objectName="Main Schedule",
        presentValue=Real(20.0),
        effectivePeriod=DateRange(
            startDate=Date(year=2025, month=1, day=1),
            endDate=Date(year=2025, month=12, day=31)
        ),
        weeklySchedule=[],
        listOfObjectPropertyReferences=[
            DeviceObjectPropertyReference(
                objectIdentifier=("analogValue", 1),
                propertyIdentifier="presentValue",
                deviceIdentifier=device.objectIdentifier
            )
        ],
        priorityForWriting=16,
        outOfService=False,
    )

    app.add_object(ai_temp)
    app.add_object(ai_hum)
    app.add_object(ai_pres)
    app.add_object(calendar)
    app.add_object(schedule)

    def updater():
        while True:
            if registry.get_sensor("temperature"):
                sensor = registry.get_sensor("temperature")
                ai_temp.presentValue = Real(sensor.value)
                ai_temp.priorityArray = sensor.priority_array
            
            if registry.get_sensor("humidity"):
                sensor = registry.get_sensor("humidity")
                ai_hum.presentValue = Real(sensor.value)
                ai_hum.priorityArray = sensor.priority_array

            if registry.get_sensor("pressure"):
                sensor = registry.get_sensor("pressure")
                ai_pres.presentValue = Real(sensor.value)
                ai_pres.priorityArray = sensor.priority_array
                
            time.sleep(1)

    threading.Thread(target=updater, daemon=True).start()
    run()
