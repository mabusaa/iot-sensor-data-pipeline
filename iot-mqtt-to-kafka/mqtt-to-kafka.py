import os
import json
import signal
import time
import paho.mqtt.client as mqtt
from kafka import KafkaProducer

# Read configuration from environment variables
MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_TOPIC = os.getenv('MQTT_TOPIC', 'sensor-data')

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'sensor-data')

# Initialize Kafka producer
producer = KafkaProducer(bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Initialize MQTT Client
client = mqtt.Client()

# Callback for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Connection failed with code {rc}")

# Callback for when a message is received from MQTT
def on_message(client, userdata, msg):
    try:
        # Decode MQTT message
        sensor_data = json.loads(msg.payload.decode())
        print(f"Received from MQTT: {sensor_data}")
        
        # Send message to Kafka
        producer.send(KAFKA_TOPIC, value=sensor_data)
        producer.flush()
        print(f"Sent to Kafka: {sensor_data}")
        
    except Exception as e:
        print(f"Error processing message: {e}")

# Callback for logging
def on_log(client, userdata, level, buf):
    print(f"Log: {buf}")

client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log

# Try to connect to the MQTT broker
try:
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
except Exception as e:
    print(f"Failed to connect to MQTT Broker: {e}")
    exit(1)

# Signal handler for exiting the program
def signal_handler(sig, frame):
    print("Exiting...")
    client.loop_stop()  # Stop the MQTT loop
    producer.close()  # Close the Kafka producer
    exit(0)

if __name__ == "__main__":
    client.loop_start()  # Start the MQTT loop
    signal.signal(signal.SIGINT, signal_handler)  # Handle CTRL+C
    while True:
        # Keep the main thread alive to handle incoming MQTT messages
        signal.pause()