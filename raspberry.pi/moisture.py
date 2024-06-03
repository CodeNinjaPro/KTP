import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)
sensor_pin = 17
GPIO.setup(sensor_pin, GPIO.IN)

while True:
    if GPIO.input(sensor_pin):
        print("Soil is dry")
    else:
        print("Soil is wet")
    time.sleep(1)
