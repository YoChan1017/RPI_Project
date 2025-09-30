import RPi.GPIO as GPIO 
import time

button_pin = 27

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    if GPIO.input(button_pin) == GPIO.LOW:  
        print("Button pushed!")
        time.sleep(0.3)  
