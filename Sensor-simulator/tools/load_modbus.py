from pymodbus.client import ModbusTcpClient
import time

def run():
    client = ModbusTcpClient("localhost", port=5020)
    client.connect()

    start = time.time()
    for _ in range(10000):
        client.read_input_registers(0, count=10)

    elapsed = time.time() - start
    rps = 10000 / elapsed
    print("Reads/sec:", rps)
    client.close()
    return rps

if __name__ == "__main__":
    run()
