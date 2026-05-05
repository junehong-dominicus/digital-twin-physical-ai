from prometheus_client import start_http_server
from metrics import *

def main():
    start_http_server(9100)

    while True:
        sensor_value.labels("temp_room_1", "C").set(22.5)
        bacnet_present_value.labels("AV:1").set(22)
        bacnet_active_priority.labels("AV:1").set(8)
