from bacpypes.pdu import Address
from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject
from bacpypes.apdu import ReadPropertyRequest, ReadPropertyACK, WritePropertyRequest, SimpleAckPDU, ErrorPDU
from bacpypes.core import run, stop, enable_sleeping
from bacpypes.primitivedata import Real, Null
from bacpypes.iocb import IOCB
import threading
import pytest
import time
import bacpypes.core

@pytest.fixture(autouse=True)
def reset_bacpypes():
    if getattr(bacpypes.core, "_task_manager", None):
        bacpypes.core._task_manager = None
    pass

def test_bacnet_priority_workflow():
    enable_sleeping()
    
    local_device = LocalDeviceObject(
        objectName="PriorityTestClient",
        objectIdentifier=55557,
        maxApduLengthAccepted=1024,
        segmentationSupported="segmentedBoth",
        vendorIdentifier=15,
    )
    
    app = BIPSimpleApplication(local_device, "127.0.0.1:47811")
    t_addr = Address("127.0.0.1:47812")

    t = threading.Thread(target=run, daemon=True) # daemon to avoid hang if thread doesn't stop
    t.start()
    
    # 1. Write Priority 8 = 50.0
    print("Writing Priority 8...")
    req_write1 = WritePropertyRequest(
        objectIdentifier=("analogValue", 1),
        propertyIdentifier="presentValue",
        propertyValue=Real(50.0),
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
        objectIdentifier=("analogValue", 1),
        propertyIdentifier="presentValue"
    )
    req_read1.pduDestination = t_addr
    iocb_r1 = IOCB(req_read1)
    app.request_io(iocb_r1)
    iocb_r1.wait(timeout=5)
    assert iocb_r1.ioResponse.propertyValue.value == 50.0, f"Expected 50.0, got {iocb_r1.ioResponse.propertyValue.value if iocb_r1.ioResponse else 'None'}"

    # 2. Write Priority 10 = 30.0
    print("Writing Priority 10...")
    req_write2 = WritePropertyRequest(
        objectIdentifier=("analogValue", 1),
        propertyIdentifier="presentValue",
        propertyValue=Real(30.0),
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
        objectIdentifier=("analogValue", 1),
        propertyIdentifier="presentValue"
    )
    req_read2.pduDestination = t_addr
    iocb_r2 = IOCB(req_read2)
    app.request_io(iocb_r2)
    iocb_r2.wait(timeout=3)
    assert iocb_r2.ioResponse.propertyValue.value == 50.0, f"Expected 50.0 preserved, got {iocb_r2.ioResponse.propertyValue.value}"

    # 3. Relinquish Priority 8 (Write Null)
    print("Relinquishing Priority 8...")
    req_write3 = WritePropertyRequest(
        objectIdentifier=("analogValue", 1),
        propertyIdentifier="presentValue",
        propertyValue=Null(),
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
        objectIdentifier=("analogValue", 1),
        propertyIdentifier="presentValue"
    )
    req_read3.pduDestination = t_addr
    iocb_r3 = IOCB(req_read3)
    app.request_io(iocb_r3)
    iocb_r3.wait(timeout=3)
    assert iocb_r3.ioResponse.propertyValue.value == 30.0, f"Expected 30.0 (Pri 10), got {iocb_r3.ioResponse.propertyValue.value}"

    stop()
    # t.join() # Might hang if stop() doesn't work perfectly. thread is daemon.
