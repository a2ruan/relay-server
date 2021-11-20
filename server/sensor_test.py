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
        #GPIO.output(power_pin_3v,True)
        time.sleep(0.0005) # this takes approx 10ms to read each pin's status.
        value = GPIO.input(pin)
        sum += value
        #print(value)
    sum = sum/samples
    if sum > 0.5:
        sum = "OFF"
    else:
        sum = "ON" 
    return sum


if __name__ == "__main__":
    #GPIO.cleanup()
    GPIO.setmode(GPIO.BOARD)
    relay_pin = 33
    sensor_pin = 31
    power_pin_3v = 32

    GPIO.setup(relay_pin,GPIO.OUT)

    GPIO.setup(power_pin_3v,GPIO.OUT)
    GPIO.output(power_pin_3v,True)

#do some stuff
    GPIO.setup(sensor_pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #GPIO.setup(sensor_pin,GPIO.IN)
    counter = 0
    good_counts = 0
    bad_counts = 0
    counts = 0
    min = 1
    max = 0
    while True:
        counter += 1
        counts += 1
        #print("Loop " + str(counter))
        #x = raw_input()
        #time.sleep(0.01)
        #GPIO.output(relay_pin,True)
        t = time.time()
        sensor_value = get_averaged_value(sensor_pin)
        elapsed_time = time.time() - t
        if sensor_value < min:
            min = sensor_value
        if sensor_value > max:
            max = sensor_value
        if sensor_value > 0.001:
            good_counts += 1
            if good_counts%1000 > 0:
                print("Count = " + str(counts) + " : " + "Good counts = " + str(good_counts) + " : Bad counts = " + str(bad_counts) + " Value = " + str(sensor_value) + " Time Elapsed = " + str(elapsed_time) + " min = " + str(min) + " max = " + str(max))
        else:
            bad_counts += 1
            print("Count = " + str(counts) + " : " + "Good counts = " + str(good_counts) + " : Bad counts = " + str(bad_counts) + " Value = " + str(sensor_value) + " Time Elapsed = " + str(elapsed_time) + " -- BAD min = " + str(min) + " max = " + str(max))
        
        
        #print("Sensor Value for pin " + str(sensor_pin) + " is: " + str(sensor_value)) 
        ''' 
        sensor_pins_to_test = [5,11,15,21,29,37,16,22,26,40]

        for i in sensor_pins_to_test:
            GPIO.setup(i,GPIO.IN)
            kk = get_averaged_value(i)
            print(kk)

        relay_pins_to_test = [3,7,13,19,23,35,12,18,24,38]

        for i in relay_pins_to_test:
            GPIO.setup(i,GPIO.OUT)
            GPIO.output(i,True)
            time.sleep(0.01)
            GPIO.output(i,False)
        '''

        if counts >200 and counts <220:
            print("ping")
            GPIO.output(33,True)
        else:
            GPIO.output(33,False)
        #print("Loop " + str(counter))
        #x = raw_input()
        #time.sleep(0.01)
        #GPIO.output(relay_pin,False)
        if counts == 1600:
            GPIO.output(33,True)
            time.sleep(10)
            counts = 0
        
print("cleaning pins")
GPIO.cleanup()
