from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import threading
import time

def run_modbus(registry, port=5020):
    # Sort sensors by name to ensure deterministic register mapping
    sensors = sorted(registry.sensors.values(), key=lambda s: s.name)
    
    # Allocate Input Registers: 2 registers per sensor (Float32)
    store = ModbusSlaveContext(
        ir=ModbusSequentialDataBlock(0, [0] * (len(sensors) * 2))
    )
    context = ModbusServerContext(slaves=store, single=True)

    def updater():
        while True:
            builder = BinaryPayloadBuilder(byteorder=Endian.BIG)
            for sensor in sensors:
                builder.add_32bit_float(sensor.value)
            regs = builder.to_registers()
            store.setValues(4, 0, regs)
            time.sleep(1)

    threading.Thread(target=updater, daemon=True).start()
    StartTcpServer(context=context, address=("0.0.0.0", port))
