import threading
import shutil
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import os
import time
import asyncio
import tarfile
from fastapi.middleware.cors import CORSMiddleware

# Internal Python Modules
# Import board state to keep track of user inputs, outputs ect.
from switch import *
from gpio import *  # Import pin I/O module to directly read/write to GPIO pins

templates = Jinja2Templates(directory="..")

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLOCK_RATE_SECONDS = 0.5

def init_pins():  # Initialize relay and sensor pins to default values
    for i in Board.switch_pair_map:
        # Get pin pairs
        relay_pin = Board.switch_pair_map.get(i)[0]
        sensor_pin = Board.switch_pair_map.get(i)[1]
        placeholder = get_pin(sensor_pin)
        # By default, set to 0 so computer doesn't accidently reset.
        set_pin(relay_pin, 0)



def update_pins(board):
    '''
    Updates the GPIO pins by reading the user-defined Board state and writing the changes to hardware.
    '''
    print("-----")
    for switch in board.get_switches():  # iterate through each switch pair
        # Read pin id and relay state
        relay_pin = switch.get_relay_pin()
        relay_value = switch.get_relay_value()
        sensor_pin = switch.get_sensor_pin()
        toggle_enabled = switch.get_toggle_enabled()
        reboot_enabled = switch.get_reboot_enabled()

        if toggle_enabled:  # Check if toggle mode is on for the first time
            # putting inside if statement to reduce lag by specifying precondition
            toggle_time_start = float(
                switch.get_toggle_time_start_milliseconds())
            toggle_time_milliseconds = float(switch.get_toggle_time())

            # PULSE SEQUENCING FOR TOGGLING A BUTTON
            # STAGE 1: BETWEEN 0 ~ toggle_time = OFF
            # STAGE 2: BETWEEN toggle_time and 2*toggle_time = ON
            # STAGE 3: AFTER toggle_time = OFF
            current_time = time.time()*1000

            if toggle_time_start <= float(0):  # STAGE 1
                switch.set_toggle_time_start_milliseconds(time.time()*1000)
                switch.set_relay_value(0)
            elif (current_time - toggle_time_start) < toggle_time_milliseconds:
                switch.set_relay_value(0)  # STAGE 1
                # print("B")
            elif (current_time - toggle_time_start) >= toggle_time_milliseconds and (current_time - toggle_time_start) < 2*toggle_time_milliseconds:
                switch.set_relay_value(1)
                # print("C")# STAGE 2
            elif (current_time - toggle_time_start) >= 2*toggle_time_milliseconds:  # STAGE 3
                # print("D")
                switch.set_toggle(False)
                switch.set_toggle_time_start_milliseconds(float(-1))
                switch.set_relay_value(0)

        # Update relay state to device
        if relay_value == 1:
            set_pin(relay_pin, 1)
        elif relay_value == 0:
            set_pin(relay_pin, 0)

        # Read and update sensor value from device
        sensor_value = get_pin(sensor_pin)
        time.sleep(0.01)
        switch.set_sensor_value(sensor_value)
        print(f"{sensor_pin}:{sensor_value}")
        # print("sensor value = " + str(sensor_value))
        # check if auto mode is on.  Auto mode on means that toggle should continously run if system is off.
        if reboot_enabled and sensor_value < 0.5:
            switch.set_toggle(True)
        

@app.get("/api/{relay_name}/{command}")
def get2(request: Request, relay_name, command):
    try:
        print(command)
        print(relay_name)
        if command == "status":
            print("\nUser requested relay " + relay_name + " state")
            time.sleep(CLOCK_RATE_SECONDS*10)
            return sb.get_switches_as_dict()[relay_name]

        elif command == "close":
            print("\nSetting relay " + relay_name + " to ON")
            for switch in sb.get_switches():
                if switch.get_name() == relay_name:
                    switch.set_relay_value(1)
            time.sleep(CLOCK_RATE_SECONDS*10)
            return {"Status":"Success"}
            #return sb.get_switches_as_dict()[relay_name]

        elif command == "open":
            print("\nSetting relay " + relay_name + " to OFF")
            for switch in sb.get_switches():
                print(switch)
                if switch.get_name() == relay_name:
                    switch.set_relay_value(0)
            time.sleep(CLOCK_RATE_SECONDS*10)
            return {"Status":"Success"}
            #return sb.get_switches_as_dict()[relay_name]

        elif command.find('name=') == 0:
            command = command[5:]
            print("Changing relay name to: " + command)
            print(not command)
            for switch in sb.get_switches():
                print("Setting new name")
                if switch.get_name() == relay_name:
                    switch.set_name(command)
            time.sleep(CLOCK_RATE_SECONDS*10)
            return sb.get_switches_as_dict()[command]

        elif command.find('toggle-time=') == 0:
            if command[12:].isdigit():
                toggle_time = int(command[12:])
                for switch in sb.get_switches():
                    if switch.get_name() == relay_name:
                        print("Setting new toggle time:" + str(toggle_time))
                        switch.set_toggle_time(toggle_time)
            else:
                print("Entry not a number")
            time.sleep(CLOCK_RATE_SECONDS*10)
            return sb.get_switches_as_dict()[relay_name]

        elif command == 'toggle':  # TBD
            for switch in sb.get_switches():
                if switch.get_name() == relay_name:
                    switch.set_toggle(True)
                    print("Toggling pin" + str(relay_name))
            time.sleep(CLOCK_RATE_SECONDS*10)
            return {"Status":"Success"}
            #return sb.get_switches_as_dict()[relay_name]

        elif command == 'auto=on':
            for switch in sb.get_switches():
                print("Setting auto to on")
                if switch.get_name() == relay_name:
                    switch.set_reboot(True)
            time.sleep(CLOCK_RATE_SECONDS*10)
            return {"Status":"Success"}
            #return sb.get_switches_as_dict()[relay_name]

        elif command == 'auto=off':
            for switch in sb.get_switches():
                print("Setting auto to off")
                if switch.get_name() == relay_name:
                    switch.set_reboot(False)
            time.sleep(CLOCK_RATE_SECONDS*10)
            return {"Status":"Success"}
            #return sb.get_switches_as_dict()[relay_name]

        return {"error": "error.  invalid entry"}
    except:
        return {"error": "error. Unexpected error."}


@app.get("/")
@app.get("/api/reports-list")
def reports_list(request: Request):
    return {"Results": "Hello World"}

@app.get("/status")
def status(request: Request):
    status = {}
    print("\nUser requested switchboard state")
    update_pins(sb)
    return sb.get_switches_as_dict()
    return status

def init_webserver(board):
    '''
    Need some sort of protection mechanism such that while this
    thread is running, there are no reads/writes from https.  
    Will wait until cycle is completed.'''
    counter_clock = 0
    while True:
        if counter_clock %100 == 0:
            print(counter_clock)
        time.sleep(CLOCK_RATE_SECONDS)  # polling frequency is 10ms.
        counter_clock += 1
        # now = datetime.now()t
        # current_time = now.strftime("%d/%m/%Y %H:%M:%S")
        # print("Current Time", current_time)
        update_pins(board)  # update GPIO states

# Initialization
from uuid import getnode as get_mac
mac = str(hex(get_mac())).replace("0x","")
target_hostname = "RPI-" + mac.upper()
print(target_hostname)
os.system(f"sudo hostnamectl set-hostname \"{target_hostname}\"")
import socket
print(socket.gethostname())

sb = Board(mac)  # Initialize board
init_gpio()  # Initialize board numbering
init_pins()  # Initialize pins on Raspberry PI to either input or output type

server = threading.Thread(target=init_webserver, args=(sb,))
server.start()

# Initialize seperate thread to read/write pin values to board at a set interval
# server = threading.Thread(target=init_webserver,args=(sb,))
# server.start()
"""
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=10000, reload=True)
"""
# if __name__ == "__main__":
#    print("Hello World!")
