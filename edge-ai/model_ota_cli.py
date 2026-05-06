import serial
import time
import sys
import os
import argparse
import paho.mqtt.client as mqtt
import base64

# EHIF Command IDs
CMD_AI_MODEL_START = 0xA3
CMD_AI_MODEL_DATA = 0xA4
CMD_AI_MODEL_END = 0xA5

def send_ehif_serial(ser, cmd, payload=b""):
    sof = 0xA5
    ver = 0x01
    seq = 0x00
    length = len(payload)
    header = bytes([sof, ver, cmd, seq, (length >> 8) & 0xFF, length & 0xFF])
    checksum = 0
    for b in header + payload:
        checksum ^= b
    
    packet = header + payload + bytes([checksum])
    ser.write(packet)
    time.sleep(0.05)

def ota_serial(port, file_path, target_type=0):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return

    file_size = os.path.getsize(file_path)
    print(f"Streaming {file_path} ({file_size} bytes) via Serial to {port}...")

    try:
        ser = serial.Serial(port, 115200, timeout=1)
        
        # START
        send_ehif_serial(ser, CMD_AI_MODEL_START, bytes([target_type]))
        print("START sent.")
        time.sleep(1)

        # DATA
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(256)
                if not chunk: break
                send_ehif_serial(ser, CMD_AI_MODEL_DATA, chunk)
                sys.stdout.write(".")
                sys.stdout.flush()
        
        print("\nDATA sent.")
        send_ehif_serial(ser, CMD_AI_MODEL_END)
        print("END sent.")
        ser.close()
    except Exception as e:
        print(f"Serial Error: {e}")

def ota_mqtt(broker, topic, file_path, target_type=0):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return

    file_size = os.path.getsize(file_path)
    print(f"Streaming {file_path} ({file_size} bytes) via MQTT to {broker}...")

    client = mqtt.Client()
    client.connect(broker, 1883, 60)
    client.loop_start()

    # MQTT Payload wraps EHIF in JSON or Base64 for easier handling by Gateway
    def publish_chunk(cmd, payload=b""):
        msg = {
            "cmd": cmd,
            "type": target_type,
            "data": base64.b64encode(payload).decode()
        }
        client.publish(topic, str(msg))
        time.sleep(0.1) # Throttling for MQTT stability

    # START
    publish_chunk(CMD_AI_MODEL_START)
    print("START sent.")
    time.sleep(2)

    # DATA
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(512) # Larger chunks for MQTT
            if not chunk: break
            publish_chunk(CMD_AI_MODEL_DATA, chunk)
            sys.stdout.write("#")
            sys.stdout.flush()

    print("\nDATA sent.")
    publish_chunk(CMD_AI_MODEL_END)
    print("END sent.")
    
    client.loop_stop()
    client.disconnect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Industrial Edge AI Model OTA Tool")
    parser.add_init = parser.add_argument_group("Target Options")
    parser.add_argument("--mode", choices=["serial", "mqtt"], default="serial", help="Transport mode")
    parser.add_argument("--port", help="Serial port (e.g. COM3 or /dev/ttyUSB0)")
    parser.add_argument("--broker", default="localhost", help="MQTT Broker address")
    parser.add_argument("--topic", default="dtpa/cmd/model_update", help="MQTT Topic")
    parser.add_argument("--file", required=True, help="Path to .tflite or .joblib file")
    parser.add_argument("--type", type=int, default=0, help="0: TFLite Model, 1: Normalization Metadata")

    args = parser.parse_args()

    print("------------------------------------------")
    print(" Industrial Edge AI OTA Deployment Tool   ")
    print("------------------------------------------")

    if args.mode == "serial":
        if not args.port:
            print("Error: --port required for serial mode")
        else:
            ota_serial(args.port, args.file, args.type)
    else:
        ota_mqtt(args.broker, args.topic, args.file, args.type)
    
    print("\nDeployment sequence finished.")

