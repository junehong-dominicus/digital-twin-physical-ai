from bacpypes.pdu import Address, GlobalBroadcast
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.object import AnalogInputObject, CalendarObject, ScheduleObject
from bacpypes.apdu import ReadPropertyRequest, ReadPropertyACK
from bacpypes.core import run, stop, enable_sleeping
from bacpypes.primitivedata import CharacterString, Real, Date
from bacpypes.constructeddata import Any
from bacpypes.basetypes import DateRange, DailySchedule, DeviceObjectPropertyReference
from bacpypes.iocb import IOCB
import threading
import time
import pytest

import asyncore
import bacpypes.core

# Mock Registry for testing
class MockRegistry:
    def get(self, key):
        return 0.0
    def snapshot(self):
        return {"temperature": 0.0, "humidity": 0.0, "pressure": 0.0}
    def by_bacnet_instance(self, inst):
        return None

@pytest.fixture(autouse=True)
def reset_bacpypes():
    # Ensure clean state
    if getattr(bacpypes.core, "_task_manager", None):
        bacpypes.core._task_manager = None
    pass

def test_bacnet_schedule_workflow():
    enable_sleeping()
    
    # Client setup
    local_device = LocalDeviceObject(
        objectName="TestClient",
        objectIdentifier=55555,
        maxApduLengthAccepted=1024,
        segmentationSupported="segmentedBoth",
        vendorIdentifier=15,
    )
    
    # Bind to a different port to avoid conflict
    app = BIPSimpleApplication(local_device, "127.0.0.1:47815")

    # Server setup (Simulator)
    server_device = LocalDeviceObject(
        objectName="SensorSimulator",
        objectIdentifier=11111,
        maxApduLengthAccepted=1024,
        segmentationSupported="segmentedBoth",
        vendorIdentifier=15,
    )
    server_app = BIPSimpleApplication(server_device, "127.0.0.1:47812")

    # Add objects
    cal = CalendarObject(
        objectIdentifier=("calendar", 1),
        objectName="Holidays",
        dateList=[]
    )
    server_app.add_object(cal)

    sch = ScheduleObject(
        objectIdentifier=("schedule", 1),
        objectName="Main Schedule",
        presentValue=Any(Real(0.0)),
        effectivePeriod=DateRange(startDate=Date((124, 1, 1, 1)), endDate=Date((124, 12, 31, 2))),
        weeklySchedule=[DailySchedule(daySchedule=[]) for _ in range(7)],
        exceptionSchedule=[],
        listOfObjectPropertyReferences=[
            DeviceObjectPropertyReference(objectIdentifier=("analogValue", 1), propertyIdentifier="presentValue", deviceIdentifier=None)
        ],
        priorityForWriting=8,
        statusFlags=[0, 0, 0, 0],
        reliability="noFaultDetected",
        outOfService=False
    )
    server_app.add_object(sch)

    # Target Address (local server)
    t_addr = Address("127.0.0.1:47812")

    # Start the IO loop in a separate thread
    t = threading.Thread(target=run, daemon=True)
    t.start()
    
    try:
        # 1. Read Calendar Object Name
        request1 = ReadPropertyRequest(
            objectIdentifier=("calendar", 1),
            propertyIdentifier="objectName"
        )
        request1.pduDestination = t_addr

        iocb1 = IOCB(request1)
        app.request_io(iocb1)
        
        iocb1.wait(timeout=5)
        if iocb1.ioError:
            pytest.fail(f"Calendar Read failed: {iocb1.ioError}")
        
        response1 = iocb1.ioResponse
        assert isinstance(response1, ReadPropertyACK)
        assert response1.propertyValue.cast_out(CharacterString) == "Holidays"

        # 2. Read Schedule Object Name
        request2 = ReadPropertyRequest(
            objectIdentifier=("schedule", 1),
            propertyIdentifier="objectName"
        )
        request2.pduDestination = t_addr

        iocb2 = IOCB(request2)
        app.request_io(iocb2)
        
        iocb2.wait(timeout=5)
        if iocb2.ioError:
            pytest.fail(f"Schedule Read failed: {iocb2.ioError}")
            
        response2 = iocb2.ioResponse
        assert response2.propertyValue.cast_out(CharacterString) == "Main Schedule"
        
    finally:
        stop()
        asyncore.close_all()
        t.join(timeout=2)
