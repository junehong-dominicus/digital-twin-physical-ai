from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import threading
import time

def on_write_register(address, value):
    reg = modbus_map[address]
    sensor = registry.get(reg["sensor"])
    if reg["writable"]:
        sensor.set_override(value * reg["scale"])

def run_modbus(registry):
    store = ModbusSlaveContext(
        ir=ModbusSequentialDataBlock(0, [0] * 100)
    )
    context = ModbusServerContext(slaves=store, single=True)

    def updater():
        while True:
            snapshot = registry.snapshot()
            builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
            builder.add_32bit_float(snapshot["temperature"])
            builder.add_32bit_float(snapshot["humidity"])
            builder.add_32bit_float(snapshot["pressure"])
            regs = builder.to_registers()
            store.setValues(4, 0, regs)
            time.sleep(1)

    threading.Thread(target=updater, daemon=True).start()
    StartTcpServer(context=context, address=("0.0.0.0", 5020))
