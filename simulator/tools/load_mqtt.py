import paho.mqtt.client as mqtt
import time

client = mqtt.Client()
client.connect("localhost", 1883)
client.loop_start()

start = time.time()
for i in range(5000):
    client.publish("sim/load/test", str(i))

print("Publishes/sec:", 5000 / (time.time() - start))
