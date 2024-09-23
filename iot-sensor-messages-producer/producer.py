import os
import json
import random
import time
import signal
import paho.mqtt.client as mqtt

# Read EMQX (MQTT) configuration from environment variables
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'sensor-data')

# Initialize MQTT Client
client = mqtt.Client()

# Callback for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print(f"Connection failed with code {rc}")

# Callback for when a message is published
def on_publish(client, userdata, mid):
    print(f"Message {mid} published.")

# Callback for logging
def on_log(client, userdata, level, buf):
    print(f"Log: {buf}")

client.on_connect = on_connect
client.on_publish = on_publish
client.on_log = on_log

# Try to connect to the broker
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f"Failed to connect to MQTT Broker: {e}")
    exit(1)

# Produce sensor data every 5 seconds
def produce_sensor_data():
    while True:
        # Simulate sensor data
        sensor_data = {
            'sensor_id': "sensor_1",
            'temperature': random.uniform(20.0, 30.0),
            'humidity': random.uniform(30.0, 70.0),
            'timestamp': time.time()
        }
        
        # Publish data to the MQTT topic
        result = client.publish(MQTT_TOPIC, json.dumps(sensor_data))
        
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            print(f"Failed to publish message: {result.rc}")
        else:
            print(f"Produced: {sensor_data}")
        
        time.sleep(5)  # Produce data every 5 seconds

# Signal handler for exiting the program
def signal_handler(sig, frame):
    print("Exiting...")
    client.loop_stop()  # Stop the MQTT loop
    exit(0)

if __name__ == "__main__":
    client.loop_start()  # Start the MQTT loop
    signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL+C
    produce_sensor_data()
