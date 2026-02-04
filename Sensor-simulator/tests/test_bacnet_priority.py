from bacpypes.pdu import Address
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.apdu import ReadPropertyRequest, ReadPropertyACK, WritePropertyRequest, SimpleAckPDU, ErrorPDU
from bacpypes.core import run, stop, enable_sleeping
from bacpypes.primitivedata import Real, Null, Date, CharacterString, Time, TagList, Boolean
from bacpypes.iocb import IOCB
from bacpypes.constructeddata import Any, ArrayOf
from bacpypes.object import AnalogValueObject, AnalogOutputObject, CalendarObject, ScheduleObject, NotificationClassObject, Property
from bacpypes.local.object import Commandable
from bacpypes.basetypes import DateRange, DailySchedule, DeviceObjectPropertyReference, PriorityArray, PriorityValue, TimeValue, LimitEnable, EventTransitionBits, NotifyType, TimeStamp, Destination, EventState
import threading
import pytest
from bacpypes.task import RecurringTask
import time
import bacpypes.core
import asyncore
# Handle case where Commandable might be a factory function
CmdMixin = Commandable
if not isinstance(Commandable, type):
    CmdMixin = Commandable(Real)

# Use the metaclass of AnalogOutputObject to resolve conflict with Commandable (which uses type)
class CommandableAnalogOutputObject(CmdMixin, AnalogOutputObject, metaclass=type(AnalogOutputObject)):
    pass

class OutOfRangeAlgorithm:
    """
    Simple implementation of the OutOfRange algorithm for BACnet objects.
    Monitors presentValue and updates eventState based on limits.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Hook into the property monitor system of bacpypes
        self._property_monitors["presentValue"].append(self.check_event_state)

    def check_event_state(self, old_value, new_value):
        limit_enable = self.limitEnable
        low_limit = self.lowLimit
        high_limit = self.highLimit
        deadband = self.deadband
        current_state = self.eventState
        
        new_state = current_state

        # Check High Limit (Bit 1 of LimitEnable)
        if limit_enable[1]: 
            if current_state == "highLimit":
                if new_value < (high_limit - deadband):
                    new_state = "normal"
            else:
                if new_value > high_limit:
                    new_state = "highLimit"
        
        # Check Low Limit (Bit 0 of LimitEnable)
        if limit_enable[0]:
            if current_state == "lowLimit":
                if new_value > (low_limit + deadband):
                    new_state = "normal"
            else:
                if new_value < low_limit:
                    new_state = "lowLimit"

        if new_state != current_state:
            self.eventState = new_state

class ReportingAnalogOutputObject(OutOfRangeAlgorithm, CmdMixin, AnalogOutputObject, metaclass=type(AnalogOutputObject)):
    pass

class WritableScheduleObject(ScheduleObject):
    properties = [
        Property("weeklySchedule", ArrayOf(DailySchedule), optional=True, mutable=True)
    ]

class SimpleScheduleEngine(RecurringTask):
    def __init__(self, app):
        super().__init__(1000)
        self.app = app
        self.install_task()

    def process_task(self):
        # Mock engine: Apply Schedule 1 to AnalogOutput 1
        sch = self.app.get_object_id(("schedule", 1))
        ao = self.app.get_object_id(("analogOutput", 1))
        
        if sch and ao and not sch.outOfService and sch.weeklySchedule:
            try:
                # Extract value (88.0) from the test schedule structure
                val = sch.weeklySchedule[0].daySchedule[0].value
                if isinstance(val, Any):
                    val = val.cast_out(Real)
                
                # Handle case where cast_out returns a Real object instead of float
                if hasattr(val, 'value'):
                    val = val.value
                    
                ao.WriteProperty('presentValue', val, priority=8)
            except Exception:
                pass

@pytest.fixture(scope="module")
def bacnet_server():
    # Ensure a clean state for the singleton core
    if getattr(bacpypes.core, "_task_manager", None):
        bacpypes.core._task_manager = None

    # 1. Setup Server Device & App
    server_device = LocalDeviceObject(
        objectName="SensorSimulator",
        objectIdentifier=11111,
        maxApduLengthAccepted=1024,
        segmentationSupported="segmentedBoth",
        vendorIdentifier=15,
    )
    server_app = BIPSimpleApplication(server_device, "127.0.0.1:47812")

    # Start the schedule engine
    _ = SimpleScheduleEngine(server_app)

    # 2. Add Objects (Required for the test to write to them)
    ao1 = CommandableAnalogOutputObject(
        objectIdentifier=("analogOutput", 1),
        objectName="ao1",
        presentValue=0.0,
        statusFlags=[0, 0, 0, 0],
        priorityArray=PriorityArray([PriorityValue(null=Null()) for _ in range(16)]),
        relinquishDefault=0.0,
    )
    server_app.add_object(ao1)

    # 3. Add Calendar Object (Required for Schedule)
    cal = CalendarObject(
        objectIdentifier=("calendar", 1),
        objectName="Holidays",
        dateList=[]
    )
    server_app.add_object(cal)

    # 4. Add Schedule Object
    # Note: We provide minimal mandatory properties
    sch = WritableScheduleObject(
        objectIdentifier=("schedule", 1),
        objectName="Main Schedule",
        presentValue=Any(Real(0.0)),
        effectivePeriod=DateRange(startDate=Date((124, 1, 1, 1)), endDate=Date((124, 12, 31, 2))), # 2024
        weeklySchedule=[DailySchedule(daySchedule=[]) for _ in range(7)],
        exceptionSchedule=[],
        listOfObjectPropertyReferences=[
            DeviceObjectPropertyReference(objectIdentifier=("analogOutput", 1), propertyIdentifier="presentValue", deviceIdentifier=None)
        ],
        priorityForWriting=8,
        statusFlags=[0, 0, 0, 0],
        reliability="noFaultDetected",
        outOfService=True
    )

    # Force mutable=True for weeklySchedule to ensure it is writable
    # This handles cases where the class override might not be sufficient due to bacpypes internals
    sch._properties["weeklySchedule"].mutable = True
    sch._properties["outOfService"].mutable = True
    server_app.add_object(sch)

    # 5. Add Analog Output with Intrinsic Reporting properties
    ao_reporting = ReportingAnalogOutputObject(
        objectIdentifier=("analogOutput", 99),
        objectName="ReportingAO",
        presentValue=25.0,
        statusFlags=[0, 0, 0, 0],
        eventState="normal",
        outOfService=False,
        units="degreesCelsius",
        priorityArray=PriorityArray([PriorityValue(null=Null()) for _ in range(16)]),
        relinquishDefault=25.0,
        # Intrinsic Reporting Properties
        notificationClass=10,
        highLimit=50.0,
        lowLimit=10.0,
        deadband=0.5,
        limitEnable=[1, 1],  # [lowLimitEnable, highLimitEnable]
        eventEnable=[1, 0, 1], # [to-offnormal, to-fault, to-normal]
        ackedTransitions=[1, 1, 1],
        notifyType="alarm",
        eventTimeStamps=[TimeStamp(time=Time((0, 0, 0, 0))) for _ in range(3)]
    )
    server_app.add_object(ao_reporting)

    # 6. Add Notification Class Object
    nc = NotificationClassObject(
        objectIdentifier=("notificationClass", 10),
        objectName="Main Notification Class",
        priority=[10, 10, 10], # Priorities for [to-offnormal, to-fault, to-normal]
        ackRequired=[1, 1, 1], # Acks required for transitions
        recipientList=[] # Empty list for now
    )
    server_app.add_object(nc)

    # 7. Start the Core Loop in a Thread
    enable_sleeping()
    t = threading.Thread(target=run, daemon=True)
    t.start()

    yield server_app

    # 4. Teardown
    stop()
    t.join()
    asyncore.close_all()

@pytest.fixture(scope="module")
def bacnet_client(bacnet_server):
    # Client depends on server to ensure loop is running
    client_device = LocalDeviceObject(
        objectName="PriorityTestClient",
        objectIdentifier=55557,
        maxApduLengthAccepted=1024,
        segmentationSupported="segmentedBoth",
        vendorIdentifier=15,
    )
    app = BIPSimpleApplication(client_device, "127.0.0.1:47814")
    return app

def test_bacnet_priority_workflow(bacnet_client):
    app = bacnet_client
    t_addr = Address("127.0.0.1:47812")

    # 1. Write Priority 8 = 50.0
    print("Writing Priority 8...")
    req_write1 = WritePropertyRequest(
            objectIdentifier=("analogOutput", 1),
        propertyIdentifier="presentValue",
        propertyValue=Any(Real(50.0)),
        priority=8
    )
    req_write1.pduDestination = t_addr
    iocb1 = IOCB(req_write1)
    app.request_io(iocb1)
    iocb1.wait(timeout=10) # Increased timeout
    assert isinstance(iocb1.ioResponse, SimpleAckPDU), f"Priority 8 Write Failed: resp={iocb1.ioResponse}, err={iocb1.ioError}"

    # Verify 50.0
    print("Verifying Priority 8...")
    req_read1 = ReadPropertyRequest(
            objectIdentifier=("analogOutput", 1),
        propertyIdentifier="presentValue"
    )
    req_read1.pduDestination = t_addr
    iocb_r1 = IOCB(req_read1)
    app.request_io(iocb_r1)
    iocb_r1.wait(timeout=5)
    assert iocb_r1.ioResponse.propertyValue.cast_out(Real) == 50.0, f"Expected 50.0, got {iocb_r1.ioResponse.propertyValue.cast_out(Real) if iocb_r1.ioResponse else 'None'}"

    # 2. Write Priority 10 = 30.0
    print("Writing Priority 10...")
    req_write2 = WritePropertyRequest(
            objectIdentifier=("analogOutput", 1),
        propertyIdentifier="presentValue",
        propertyValue=Any(Real(30.0)),
        priority=10
    )
    req_write2.pduDestination = t_addr
    iocb2 = IOCB(req_write2)
    app.request_io(iocb2)
    iocb2.wait(timeout=3)
    assert isinstance(iocb2.ioResponse, SimpleAckPDU), "Priority 10 Write Failed"

    # Verify still 50.0 (Priority 8 wins)
    print("Verifying Priority 8 dominance...")
    req_read2 = ReadPropertyRequest(
            objectIdentifier=("analogOutput", 1),
        propertyIdentifier="presentValue"
    )
    req_read2.pduDestination = t_addr
    iocb_r2 = IOCB(req_read2)
    app.request_io(iocb_r2)
    iocb_r2.wait(timeout=3)
    assert iocb_r2.ioResponse.propertyValue.cast_out(Real) == 50.0, f"Expected 50.0 preserved, got {iocb_r2.ioResponse.propertyValue.cast_out(Real)}"

    # 3. Relinquish Priority 8 (Write Null)
    print("Relinquishing Priority 8...")
    req_write3 = WritePropertyRequest(
            objectIdentifier=("analogOutput", 1),
        propertyIdentifier="presentValue",
        propertyValue=Any(Null()),
        priority=8
    )
    req_write3.pduDestination = t_addr
    iocb3 = IOCB(req_write3)
    app.request_io(iocb3)
    iocb3.wait(timeout=3)
    assert isinstance(iocb3.ioResponse, SimpleAckPDU), "Relinquish Failed"

    # Verify 30.0 (Priority 10 takes over)
    print("Verifying Priority 10 takeover...")
    req_read3 = ReadPropertyRequest(
            objectIdentifier=("analogOutput", 1),
        propertyIdentifier="presentValue"
    )
    req_read3.pduDestination = t_addr
    iocb_r3 = IOCB(req_read3)
    app.request_io(iocb_r3)
    iocb_r3.wait(timeout=3)
    assert iocb_r3.ioResponse.propertyValue.cast_out(Real) == 30.0, f"Expected 30.0 (Pri 10), got {iocb_r3.ioResponse.propertyValue.cast_out(Real)}"

def test_read_schedule_objects(bacnet_client):
    app = bacnet_client
    t_addr = Address("127.0.0.1:47812")

    # 1. Read Calendar Name
    req1 = ReadPropertyRequest(
        objectIdentifier=("calendar", 1),
        propertyIdentifier="objectName"
    )
    req1.pduDestination = t_addr
    iocb1 = IOCB(req1)
    app.request_io(iocb1)
    iocb1.wait(timeout=5)
    assert isinstance(iocb1.ioResponse, ReadPropertyACK), f"Calendar Read Failed: {iocb1.ioError}"
    assert iocb1.ioResponse.propertyValue.cast_out(CharacterString) == "Holidays"

    # 2. Read Schedule Name
    req2 = ReadPropertyRequest(
        objectIdentifier=("schedule", 1),
        propertyIdentifier="objectName"
    )
    req2.pduDestination = t_addr
    iocb2 = IOCB(req2)
    app.request_io(iocb2)
    iocb2.wait(timeout=5)
    assert isinstance(iocb2.ioResponse, ReadPropertyACK), f"Schedule Read Failed: {iocb2.ioError}"
    assert iocb2.ioResponse.propertyValue.cast_out(CharacterString) == "Main Schedule"

def test_schedule_activation(bacnet_client):
    app = bacnet_client
    t_addr = Address("127.0.0.1:47812")

    # 1. Configure Schedule to output 88.0 always
    # Time(0,0,0,0) = Midnight
    tv = TimeValue(time=Time((0, 0, 0, 0)), value=Real(88.0))
    ds = DailySchedule(daySchedule=[tv])
    # Create array for 7 days
    ws = ArrayOf(DailySchedule)([ds] * 7)

    ws_tags = TagList()
    ws.encode(ws_tags)

    sch_val = Any()
    sch_val.tagList = ws_tags

    req_write = WritePropertyRequest(
        objectIdentifier=("schedule", 1),
        propertyIdentifier="weeklySchedule",
        propertyValue=sch_val
    )
    req_write.pduDestination = t_addr

    iocb = IOCB(req_write)
    app.request_io(iocb)
    iocb.wait(timeout=10)
    assert isinstance(iocb.ioResponse, SimpleAckPDU), f"Write Schedule Failed: {iocb.ioError}"

    # 2. Enable Schedule (outOfService=False)
    req_enable = WritePropertyRequest(
        objectIdentifier=("schedule", 1),
        propertyIdentifier="outOfService",
        propertyValue=Any(Boolean(False))
    )
    req_enable.pduDestination = t_addr
    iocb_enable = IOCB(req_enable)
    app.request_io(iocb_enable)
    iocb_enable.wait(timeout=5)
    assert isinstance(iocb_enable.ioResponse, SimpleAckPDU), f"Enable Schedule Failed: {iocb_enable.ioError}"

    # 3. Wait for schedule evaluation (depends on server implementation loop)
    time.sleep(2)

    # 4. Verify AnalogOutput updated
    req_read = ReadPropertyRequest(
        objectIdentifier=("analogOutput", 1),
        propertyIdentifier="presentValue"
    )
    req_read.pduDestination = t_addr
    
    iocb_r = IOCB(req_read)
    app.request_io(iocb_r)
    iocb_r.wait(timeout=5)
    
    # Expect 88.0
    assert iocb_r.ioResponse.propertyValue.cast_out(Real) == 88.0

def test_intrinsic_reporting_props(bacnet_client):
    app = bacnet_client
    t_addr = Address("127.0.0.1:47812")

    # Verify highLimit property exists and is readable
    req = ReadPropertyRequest(
        objectIdentifier=("analogOutput", 99),
        propertyIdentifier="highLimit"
    )
    req.pduDestination = t_addr
    iocb = IOCB(req)
    app.request_io(iocb)
    iocb.wait(timeout=5)
    assert iocb.ioResponse.propertyValue.cast_out(Real) == 50.0

def test_event_detection(bacnet_client):
    app = bacnet_client
    t_addr = Address("127.0.0.1:47812")

    # 1. Write High Value (60.0 > 50.0 highLimit)
    # This should trigger the OutOfRangeAlgorithm to change eventState to 'highLimit'
    req_write = WritePropertyRequest(
        objectIdentifier=("analogOutput", 99),
        propertyIdentifier="presentValue",
        propertyValue=Any(Real(60.0)),
        priority=8
    )
    req_write.pduDestination = t_addr
    iocb = IOCB(req_write)
    app.request_io(iocb)
    iocb.wait(timeout=5)
    assert isinstance(iocb.ioResponse, SimpleAckPDU), f"Write Failed: {iocb.ioError}"

    # 2. Read Event State
    req_read = ReadPropertyRequest(
        objectIdentifier=("analogOutput", 99),
        propertyIdentifier="eventState"
    )
    req_read.pduDestination = t_addr
    iocb = IOCB(req_read)
    app.request_io(iocb)
    iocb.wait(timeout=5)
    
    # Expect "highLimit" (Enumerated value 3)
    # bacpypes typically returns the string label for Enumerated types
    assert iocb.ioResponse.propertyValue.cast_out(EventState) == "highLimit"

def test_notification_class_exists(bacnet_client):
    app = bacnet_client
    t_addr = Address("127.0.0.1:47812")

    req = ReadPropertyRequest(
        objectIdentifier=("notificationClass", 10),
        propertyIdentifier="objectName"
    )
    req.pduDestination = t_addr
    iocb = IOCB(req)
    app.request_io(iocb)
    iocb.wait(timeout=5)
    assert iocb.ioResponse.propertyValue.cast_out(CharacterString) == "Main Notification Class"
