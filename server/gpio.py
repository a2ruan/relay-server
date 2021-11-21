# This module acts as the View for the Raspberry Pi 4's pins.  This is middleware where code gets translated into hardware actions.

import RPi.GPIO as GPIO
import time

def init_gpio():
    '''
    Initializes the Raspberry PI GPIO pins based on the BOARD type numbering.
    This method must be called at the beginning of every script using this module.
    '''
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

def get_pin(pin):
    '''
    Returns the state of a sensor pin
    Input: pin = integer corresponding to pin id
    Output: value [0-1], where 0 = OFF (open-circuit), 1 = ON (voltage detected, closed-circuit)
    '''
    GPIO.setup(pin,GPIO.IN)
    return int(not(GPIO.input(pin))) # 0 if OFF, 1 if ON

def set_pin(pin, state):
    '''
    Set the voltage of a GPIO pin to 3V or 0V depending on input state
    Input: pin = integer corresponding to pin id
    state = integer [0~1], where 1 = set pin to ON, 0 = set pin to OFF
    '''
    #print("setting pin")
    if state == 1:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,True)
    else:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,False)

if __name__ == "__main__":
    print("Unit testing only.  This script may throw an error if not running on Raspberry Pi Operating System")
    
    print("Initializing board type")
    init_gpio()

    while True:
        print(get_pin(37))
        time.sleep(0.5)

    '''
    
    print("Flashing 5 times slowly on pin 36")
    for k in range(5):
        print(k)
        set_pin(36,1)
        time.sleep(1)
        set_pin(36,0)
        time.sleep(1)

    print("\nFlashing 10 times quickly on pin 36 if pin 32 is high")
    sensor = get_pin(32)
    print("Pin 32 state: " + str(sensor))
    
    if sensor:
        for k in range(10):
            print(k)
            set_pin(36,1)
            time.sleep(0.2)
            set_pin(36,0)
            time.sleep(0.2)
    '''

    
    
    
