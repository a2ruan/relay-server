# This file serves as the View for users to interact with.

# External Libraries
from flask import Flask, jsonify, request, render_template
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
import threading
from requests import get
import time
import json
from datetime import datetime

# Internal Python Modules
from switch import * # Import board state to keep track of user inputs, outputs ect.
from gpio import * # Import pin I/O module to directly read/write to GPIO pins

CLOCK_RATE_SECONDS = 0.01 # this indicates that the GPIO pins on the Raspberry Pi should be updated every 10ms

app = Flask(__name__)

class Controller(Resource):
	def get(self, command):
		print(command)
		if command == "status-dict":
			print("\nUser requested switchboard state")
			update_pins(sb)
			return jsonify(sb.get_switches_as_dict())
		return {"data":"Invalid Entry"}

class ControllerNode(Resource):
	@app.route('/')
	def get(self, relay_name, command):
		print(command)
		print(relay_name)
		sb.add_to_history(get_date(),get_time(),request.remote_addr,relay_name,command)
		print(sb.get_history())
		if command == "status":
			print("\nUser requested relay " + relay_name + " state")
			time.sleep(CLOCK_RATE_SECONDS*10)
			return sb.get_switches_as_dict()[relay_name]

		elif command == "close":
			print("\nSetting relay " + relay_name + " to ON")
			for switch in sb.get_switches():
				if switch.get_name() == relay_name: switch.set_relay_value(1)
			time.sleep(CLOCK_RATE_SECONDS*10)
			return sb.get_switches_as_dict()[relay_name]

		elif command == "open":
			print("\nSetting relay " + relay_name + " to OFF")
			for switch in sb.get_switches():
				if switch.get_name() == relay_name: switch.set_relay_value(0)
			time.sleep(CLOCK_RATE_SECONDS*10)
			return sb.get_switches_as_dict()[relay_name]	

		elif command.find('name=') == 0:
			command = command[5:]
			print("Changing relay name to: " + command)
			print(not command)
			for switch in sb.get_switches():
				print("Setting new name")
				if switch.get_name() == relay_name: switch.set_name(command)
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

		elif command == 'toggle': # TBD
			for switch in sb.get_switches():
				if switch.get_name() == relay_name: 
					switch.set_toggle(True)
					print("Toggling pin" + str(relay_name))
			time.sleep(CLOCK_RATE_SECONDS*10)
			return sb.get_switches_as_dict()[relay_name]

		elif command == 'auto=on':
			for switch in sb.get_switches():
				print("Setting auto to on")
				if switch.get_name() == relay_name: switch.set_reboot(True)
			time.sleep(CLOCK_RATE_SECONDS*10)
			return sb.get_switches_as_dict()[relay_name]

		elif command == 'auto=off':
			for switch in sb.get_switches():
				print("Setting auto to off")
				if switch.get_name() == relay_name: switch.set_reboot(False)
			time.sleep(CLOCK_RATE_SECONDS*10)
			return sb.get_switches_as_dict()[relay_name]

		return {"data":"Invalid Entry"}
	
	@app.route('/')
	def post(self, relay_name, command):
		print(self.get(relay_name,command))


@app.route('/status')
def render_status_table():
	switch_states = sb.get_switches_as_dict()
	return render_template('status_template.html',switch_states=switch_states)

@app.route('/history')
def render_history_table():
	history_ref = sb.get_history()
	history = history_ref[:]
	history.reverse()
	history_headers = sb.get_history_headers()
	return render_template('history_template.html',history=history, headers=history_headers)

def get_time(): # Returns time as a string
	now = datetime.now()
	return now.strftime("%H:%M:%S")

def get_date(): # Returns time as a string
	now = datetime.now()
	return now.strftime("%d/%m/%Y")

@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200

def init_pins(): # Initialize relay and sensor pins to default values
	for i in Board.switch_pair_map:
		# Get pin pairs
		relay_pin = Board.switch_pair_map.get(i)[0]
		sensor_pin = Board.switch_pair_map.get(i)[1]
		
		placeholder = get_pin(sensor_pin)
		set_pin(relay_pin,0) # By default, set to 0 so computer doesn't accidently reset.

def update_pins(board):
	'''
	Updates the GPIO pins by reading the user-defined Board state and writing the changes to hardware.

	'''
	for switch in board.get_switches(): # iterate through each switch pair
		# Read pin id and relay state
		relay_pin = switch.get_relay_pin()
		relay_value = switch.get_relay_value()
		sensor_pin = switch.get_sensor_pin()
		toggle_enabled = switch.get_toggle_enabled()
		reboot_enabled = switch.get_reboot_enabled()

		if toggle_enabled: # Check if toggle mode is on for the first time
			toggle_time_start = float(switch.get_toggle_time_start_milliseconds()) # putting inside if statement to reduce lag by specifying precondition
			toggle_time_milliseconds = float(switch.get_toggle_time())

			# PULSE SEQUENCING FOR TOGGLING A BUTTON
			# STAGE 1: BETWEEN 0 ~ toggle_time = OFF
			# STAGE 2: BETWEEN toggle_time and 2*toggle_time = ON
			# STAGE 3: AFTER toggle_time = OFF
			current_time = time.time()*1000
			
			if toggle_time_start <= float(0): # STAGE 1
				switch.set_toggle_time_start_milliseconds(time.time()*1000) 
				switch.set_relay_value(0)
			elif (current_time - toggle_time_start) < toggle_time_milliseconds: 
				switch.set_relay_value(0)# STAGE 1
				#print("B")
			elif (current_time - toggle_time_start) >= toggle_time_milliseconds and (current_time - toggle_time_start) < 2*toggle_time_milliseconds: 
				switch.set_relay_value(1) 
				#print("C")# STAGE 2
			elif (current_time - toggle_time_start) >= 2*toggle_time_milliseconds: # STAGE 3
				#print("D")
				switch.set_toggle(False)
				switch.set_toggle_time_start_milliseconds(float(-1))
				switch.set_relay_value(0)

		# Update relay state to device
		if relay_value == 1:
			set_pin(relay_pin,1)
		elif relay_value == 0:
			set_pin(relay_pin,0)

		# Read and update sensor value from device
		sensor_value = get_pin(sensor_pin)
		switch.set_sensor_value(sensor_value)
		#print("sensor value = " + str(sensor_value))
		if reboot_enabled and sensor_value < 0.5: # check if auto mode is on.  Auto mode on means that toggle should continously run if system is off.
			switch.set_toggle(True)



def init_webserver(board):
	'''
	Need some sort of protection mechanism such that while this
	thread is running, there are no reads/writes from https.  
	Will wait until cycle is completed.
	'''
	counter_clock = 0
	while True:
		time.sleep(CLOCK_RATE_SECONDS) # polling frequency is 10ms.  
		counter_clock += 1
		#now = datetime.now()
		#current_time = now.strftime("%d/%m/%Y %H:%M:%S")
		#print("Current Time", current_time)
		update_pins(board) # update GPIO states

if __name__ == "__main__":
	print("Unit testing only:")

	sb = Board("SYSC-RPI-1") # Initialize board
	init_gpio() # Initialize board numbering 
	init_pins() # Initialize pins on Raspberry PI to either input or output type

	# Initialize seperate thread to read/write pin values to board at a set interval
	server = threading.Thread(target=init_webserver,args=(sb,))
	server.start()

	# Initialize Flask webserver to recieve REST API calls
	api = Api(app)
	api.add_resource(Controller,'/<string:command>') # REST calls for entire board
	api.add_resource(ControllerNode,'/<string:relay_name>/<string:command>') # REST calls for specific pins
	print("Starting REST API server")
	app.run(host='0.0.0.0', port = 5000,debug=False, threaded=True, use_reloader=False) # 0.0.0.0 means localhost on machine that the script is running on.