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

class Controller(Resource):
	def get(self, command):
		print(command)
		if command == "status":
			print("\nUser requested switchboard state")
			update_pins(sb)
			return sb.get_switches_as_dict()
		elif command == "update":
			print("\nUpdating pins")
			for i in sb.get_switches():
				i.set_relay_value(1)

			return sb.get_switches_as_dict()
		return {"data":"Invalid Entry"}

class ControllerNode(Resource):
	def get(self, relay_name, command):
		print(command)
		print(relay_name)
		if command == "status":
			print("\nUser requested relay " + relay_name + " state")
			update_pins(sb)
			return sb.get_switches_as_dict()[relay_name]

		elif command == "close":
			print("\nSetting relay " + relay_name + " to ON")
			for switch in sb.get_switches():
				if switch.get_name() == relay_name: switch.set_relay_value(1)
			update_pins(sb)
			return sb.get_switches_as_dict()[relay_name]

		elif command == "open":
			print("\nSetting relay " + relay_name + " to OFF")
			for switch in sb.get_switches():
				if switch.get_name() == relay_name: switch.set_relay_value(0)
			update_pins(sb)
			return sb.get_switches_as_dict()[relay_name]	

		elif command.find('name=') == 0:
			command = command[5:]
			print("Changing relay name to: " + command)
			print(not command)
			for switch in sb.get_switches():
				print("Setting new name")
				if switch.get_name() == relay_name: switch.set_name(command)
			update_pins(sb)
			return sb.get_switches_as_dict()[command]

		return {"data":"Invalid Entry"}

def init_pins(): # Initialize relay and sensor pins to default values
	for i in Board.switch_pair_map:
		# Get pin pairs
		relay_pin = Board.switch_pair_map.get(i)[0]
		sensor_pin = Board.switch_pair_map.get(i)[1]
		
		placeholder = get_pin(sensor_pin)
		set_pin(relay_pin,0) # By default, set to 0 so computer doesn't accidently reset.

def update_pins(board):
	'''
	Step 1: Read sensor pins 
	Step 2: Write sensor pin values to Board object
	Step 3: Read intended relay values from Board object
	Step 4: Write relay values to relay pins
	'''

	for switch in board.get_switches(): # iterate through each switch pair
		# Read pin id and relay state
		relay_pin = switch.get_relay_pin()
		relay_value = switch.get_relay_value()
		sensor_pin = switch.get_sensor_pin()
		
		# Update relay state to device
		if relay_value == 1:
			print(relay_pin)
			set_pin(relay_pin,1)

		# Read and update sensor value from device
		sensor_value = get_pin(sensor_pin)
		switch.set_sensor_value(sensor_value)

def init_webserver(board):
	'''
	Need some sort of protection mechanism such that while this
	thread is running, there are no reads/writes from https.  
	Will wait until cycle is completed.
	'''
	while True:
		time.sleep(2)
		now = datetime.now()
		current_time = now.strftime("%d/%m/%Y %H:%M:%S")
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
	app = Flask(__name__)
	api = Api(app)
	api.add_resource(Controller,'/<string:command>') # REST calls for entire board
	api.add_resource(ControllerNode,'/<string:relay_name>/<string:command>') # REST calls for specific pins
	print("Starting REST API server")
	app.run(host='0.0.0.0', port = 5000,debug=True, threaded=True) # 0.0.0.0 means localhost on machine that the script is running on.