try:
    from pymodbus.client import ModbusTcpClient
except ImportError:
    from pymodbus.client.sync import ModbusTcpClient

def test_temperature_register():
    client = ModbusTcpClient("localhost", port=5020)
    client.connect()
    rr = client.read_input_registers(0, count=2)
    assert rr.isError() is False
    client.close()
