from bacpypes.core import run
from bacpypes.app import BIPSimpleApplication
from bacpypes.object import AnalogInputObject
from bacpypes.local.device import LocalDeviceObject
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

    app = BIPSimpleApplication(device, "0.0.0.0/24")

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

    app.add_object(ai_temp)
    app.add_object(ai_hum)
    app.add_object(ai_pres)

    def updater():
        while True:
            ai_temp.presentValue = registry.get("temperature")
            ai_hum.presentValue = registry.get("humidity")
            ai_pres.presentValue = registry.get("pressure")
            time.sleep(1)

    threading.Thread(target=updater, daemon=True).start()
    run()
