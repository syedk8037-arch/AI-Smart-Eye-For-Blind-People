import RPi.GPIO as GPIO
import os
import time

BUTTON_PIN = 3  # GPIO3 (Pin 5)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN)

print("Shutdown button monitoring started...")

while True:
    if GPIO.input(BUTTON_PIN) == 0:   # single press detected
        print("Shutdown button pressed")
        os.system("sudo /usr/sbin/shutdown -h now")
        time.sleep(3)                 # wait so command executes
    time.sleep(0.1)
