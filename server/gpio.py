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
    #GPIO.setup(pin,GPIO.IN)
    GPIO.setup(pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    return int(not(GPIO.input(pin))) # 0 if OFF, 1 if ON

def set_pin(pin, state):
    '''
    Set the voltage of a GPIO pin to 3V or 0V depending on input state
    Input: pin = integer corresponding to pin id
    state = integer [0~1], where 1 = set pin to ON, 0 = set pin to OFF
    '''
    if state == 1:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,True)
    else:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,False)
