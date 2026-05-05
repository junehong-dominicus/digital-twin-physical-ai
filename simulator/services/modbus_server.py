from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext, ModbusSequentialDataBlock
import threading
import time
import logging
import struct

def float_to_registers(val):
    """Convert a float to two 16-bit registers (Big Endian)."""
    packed = struct.pack('>f', val)
    return struct.unpack('>HH', packed)

def run_modbus(registry, port=5020):
    # In pymodbus 3.x, ModbusSlaveContext is replaced by ModbusDeviceContext
    slaves = {}
    sensors = sorted(registry.sensors.values(), key=lambda s: s.name)
    
    for slave_id in range(1, 6): # Slaves 1, 2, 3, 4, 5
        store = ModbusDeviceContext(
            ir=ModbusSequentialDataBlock(0, [0] * (len(sensors) * 2))
        )
        slaves[slave_id] = store

    context = ModbusServerContext(slaves=slaves, single=False)

    def updater():
        while True:
            for slave_id, store in slaves.items():
                regs = []
                for sensor in sensors:
                    val = float(sensor.value) + (slave_id * 0.1)
                    regs.extend(float_to_registers(val))
                store.setValues(4, 0, regs)
            time.sleep(1)

    threading.Thread(target=updater, daemon=True).start()
    logging.info(f"Modbus Multi-Slave Server (IDs 1-5) started at 0.0.0.0:{port}")
    # In pymodbus 3.x, address is passed as a tuple to StartTcpServer
    StartTcpServer(context=context, address=("0.0.0.0", port))
