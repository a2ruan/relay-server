#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from gpio import *
import time
#Set GPIO pins as outputs

def testrelay():
    while True:
        print("Relay OFF")
        x = raw_input()
        GPIO.output(relay_pin,True)

        print("Relay ON")
        x = raw_input()
        GPIO.output(relay_pin,False)

def testauto():
    pass

if __name__ == "__main__":
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    relay_pin = 33
    GPIO.setup(relay_pin,GPIO.OUT)

    testrelay()

GPIO.cleanup()


