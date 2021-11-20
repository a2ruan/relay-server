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
        time.sleep(0.0005) # this takes approx 10ms to read each pin's status.
        value = GPIO.input(pin)
        sum += value
        #print(value)
    sum = sum/samples
    return sum


if __name__ == "__main__":
    GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)

    state = True
    GPIO.setup(32,GPIO.OUT)
    GPIO.output(32,state)

    while True:
        time.sleep(1)
        print()
        sensor_pins_to_test2 = [5,11,15,21,29,37,16,22,26,40,32,33]
        sensor_pins_to_test = [31]
        printstring = ""
        for i in sensor_pins_to_test:
            GPIO.setup(i,GPIO.IN)
            time.sleep(0.2)
            kk = str(get_averaged_value(i))
            printstring = printstring + ":" + "(" + str(i)+")" + kk
        print(printstring)
GPIO.cleanup()
