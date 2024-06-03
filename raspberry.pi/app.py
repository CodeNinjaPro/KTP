import adafruit_dht
import board
import RPi.GPIO as GPIO
import redis
import time
import json

# Configuration
DHT_PIN = board.D4  # GPIO pin connected to the DHT22 sensor
MOISTURE_PIN = 17  # GPIO pin connected to the Moisture Sensor Comparator Board
REDIS_HOST = 'localhost'  # Redis server hostname
REDIS_PORT = 6379  # Redis server port
DEVICE_ID = 1  # Device ID

# Initialize DHT22 sensor
dht_device = adafruit_dht.DHT22(DHT_PIN)

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_PIN, GPIO.IN)

# Initialize Redis client
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def read_sensors():
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        if temperature is None or humidity is None:
            return None, None, None
    except RuntimeError as err:
        print(f"DHT22 error: {err.args[0]}")
        return None, None, None

    moisture = GPIO.input(MOISTURE_PIN)
    vwc = moisture  # Example calculation; adjust as needed for your sensor
    return temperature, humidity, vwc

def broadcast_data(data):
    redis_client.publish('sensor_data', json.dumps(data))

def main():
    while True:
        temp, humidity, vwc = read_sensors()
        if temp is not None and humidity is not None:
            data = {
                "device_id": DEVICE_ID,
                "temp": temp,
                "humidity": humidity,
                "vwc": vwc
            }
            broadcast_data(data)
            print(f"Broadcasted data: {temp}°C, {humidity}%, {vwc}")
        else:
            error_message = {
                "device_id": DEVICE_ID,
                "error": "Failed to retrieve data from sensors"
            }
            broadcast_data(error_message)
            print("Broadcasted error message: Failed to retrieve data from sensors")
        time.sleep(10)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
