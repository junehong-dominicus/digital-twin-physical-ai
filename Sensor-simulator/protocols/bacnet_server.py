from bacpypes.core import run
from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogInputObject, CalendarObject, ScheduleObject
from bacpypes.local.device import LocalDeviceObject
from bacpypes.primitivedata import Real, Date, Time, Boolean
from bacpypes.basetypes import DateRange, DeviceObjectPropertyReference
import threading
import time

def do_WritePropertyRequest(self, apdu):
    handle_write_property(apdu, self.registry)

def run_bacnet(registry):
    device = LocalDeviceObject(
        objectName="SensorSimulator",
        objectIdentifier=1234,
        maxApduLengthAccepted=1024,
        segmentationSupported="segmentedBoth",
        vendorIdentifier=15,
    )

    app = BIPSimpleApplication(device, "127.0.0.1/24")

    ai_temp = AnalogInputObject(
        objectIdentifier=("analogInput", 1),
        objectName="Temperature",
        units="degreesCelsius",
        presentValue=0.0,
    )

    ai_hum = AnalogInputObject(
        objectIdentifier=("analogInput", 2),
        objectName="Humidity",
        units="percent",
        presentValue=0.0,
    )

    ai_pres = AnalogInputObject(
        objectIdentifier=("analogInput", 3),
        objectName="Pressure",
        units="pascals",
        presentValue=0.0,
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
                objectIdentifier=("analogInput", 1),
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
            ai_temp.presentValue = registry.get("temperature")
            ai_hum.presentValue = registry.get("humidity")
            ai_pres.presentValue = registry.get("pressure")
            time.sleep(1)

    threading.Thread(target=updater, daemon=True).start()
    run()
