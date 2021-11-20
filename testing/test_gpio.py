#!/usr/bin/python
import RPi.GPIO as GPIO
import time
#Set GPIO pins as outputs
GPIO.setmode(GPIO.BOARD)

pins = [2,3,4,17,27,22,10,9,11,5,6,13,19,26,18,23,25,8,7,12,16,20,21]
i = 36
for k in range(100):
	print(i)
	GPIO.setup(i,GPIO.OUT)
	GPIO.output(i,True)
	time.sleep(0.5)
	GPIO.output(i,False)
	time.sleep(0.5)

GPIO.cleanup()