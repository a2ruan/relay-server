#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from gpio import *
import time
#Set GPIO pins as outputs

def get_averaged_value(pin):
    sum = 0.00000001
    samples = 100
    for i in range(samples):
        time.sleep(0.05) # this takes approx 10ms to read each pin's status.
        value = GPIO.input(pin)
        sum += value
        print(value)
    sum = sum/samples
    return sum


if __name__ == "__main__":
    # TESTING SINGLE GPIO FUNCTION
    #GPIO.cleanup()
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

    power_pin = 32
    GPIO.setup(power_pin,GPIO.OUT)
    GPIO.output(power_pin,True)
    sensor_pin = 31
    
    while True:
        time.sleep(0.5)
        GPIO.setup(sensor_pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(GPIO.input(sensor_pin))
    # RESULTS SHOW INCONSISTENT 1 0 if no pulldown resistor.  

        
print("cleaning pins")
GPIO.cleanup()
