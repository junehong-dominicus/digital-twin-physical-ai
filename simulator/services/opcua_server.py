import asyncio
import logging
from asyncua import ua, Server
from asyncua.common.methods import uamethod

async def run_opcua(registry, port=4840):
    # Setup server
    server = Server()
    await server.init()
    server.set_endpoint(f"opc.tcp://0.0.0.0:{port}/freeopcua/server/")
    
    # Setup namespace
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # Get Objects node, this is where we should put our custom nodes
    objects = server.nodes.objects

    # Create a folder for sensors
    sensor_folder = await objects.add_folder(idx, "Sensors")

    # Mapping of sensor names to OPC-UA variables
    opc_vars = {}

    for sensor in registry.sensors.values():
        var = await sensor_folder.add_variable(idx, sensor.name, 0.0)
        await var.set_writable()  # Allow writing to sensors for control simulation
        opc_vars[sensor.name] = var

    async def updater():
        while True:
            for name, var in opc_vars.items():
                sensor = registry.get_sensor(name)
                if sensor:
                    await var.write_value(float(sensor.value))
            await asyncio.sleep(1)

    # Start the server and the updater
    async with server:
        print(f"OPC-UA Server started at opc.tcp://0.0.0.0:{port}/freeopcua/server/")
        await updater()

def start_opcua(registry, port=4840):
    """Bridge to run the async opcua server in a separate thread if needed."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_opcua(registry, port))
