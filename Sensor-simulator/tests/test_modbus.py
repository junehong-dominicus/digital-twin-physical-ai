from pymodbus.client import ModbusTcpClient

def test_temperature_register():
    client = ModbusTcpClient("localhost", port=5020)
    client.connect()
    rr = client.read_input_registers(0, 2)
    assert rr.isError() is False
    client.close()
