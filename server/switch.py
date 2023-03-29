# This module acts as the Model (database) by storing the intended state of the Raspberry Pi's pins.

class Board():
    '''
    The Board class represents the GPIO pins located on the Raspberry Pi Server.
    The Board consists of 12 pin pairs, where each pair is represented by the Relay class.
    '''

    switch_pair_map = {  # Key = switch pair number, Value = list containing relay pin and sensor pin respectively
        11: [3, 5],
        2: [7, 11],
        3: [13, 15],
        4: [19, 21],
        5: [23, 29],
        1: [33, 31],  # This is the sensor/relay pair used for testing
        7: [37, 35],
        8: [12, 16],
        9: [18, 22],
        10: [24, 26],
        6: [32, 36],
        12: [38, 40]
    }

    def __init__(self, name):
        self.name = name
        self.switches = []
        self.history_headers = ['DATE', 'TIME', 'IP', 'RELAY_GROUP', 'ACTION']
        self.history = []  # A history of all REST calls/updates
        self.max_history_size = 10000
        self.set_default_switches()

    def get_name(self): return self.name
    def get_switches(self): return self.switches
    def get_history(self): return self.history
    def get_history_headers(self): return self.history_headers
    def get_max_history_size(self): return self.max_history_size

    def set_max_history_size(
        self, max_history_size): self.max_history_size = max_history_size

    def get_switches_as_dict(self):
        switch_dict = {}
        for i, switch in enumerate(self.switches):
            switch_name = switch.get_name()
            switch_dict[switch_name] = {
                # "RELAY_NAME":"RELAY_" + '0'*(2-len(str(switch_name)))+str(switch_name),
                "PRIMARY_KEY": str(switch_name),
                "RELAY_PIN": switch.get_relay_pin(),
                "RELAY_VALUE": switch.get_relay_value(),
                "SENSOR_PIN": switch.get_sensor_pin(),
                "AUTO_REBOOT": switch.get_reboot_enabled(),
                "TOGGLE_TIME_MILLIS": switch.get_toggle_time(),
                "SENSOR_VALUE": switch.get_sensor_value()}

        return switch_dict

    def set_default_switches(self):
        for i in range(1, 13):  # Sets pins defaults from [1-12] inclusive
            switch_pair = Relay(
                self.switch_pair_map[i][0], self.switch_pair_map[i][1], str(i))
            self.switches.append(switch_pair)

    def add_to_history(self, date, time, ip, relay_group_name, action):
        if len(self.history) >= self.max_history_size:
            self.history = self.history[1:]

        self.history.append([date, time, ip, relay_group_name, action])


class Relay():
    '''
    The Relay class represents two pins: the relay pin used to relay the pwm signal 
    to restart the computer and a sensor pin used to determine if a computer is on or off.
    '''

    def __init__(self, pin_relay, pin_sensor, name):
        self.relay_value = 0
        self.name = name
        self.pin_relay = pin_relay
        self.pin_sensor = pin_sensor
        self.sensor_value = 0
        self.reboot_enabled = False

        # Toggle mode variables
        # specifies whether the relay is in a toggle state.
        self.toggle_enabled = False
        # specifies the time it takes to switch the relay to on (closed) and off (open), in milliseconds.
        self.toggle_time_milliseconds = 150
        # records down the time that a toggle was triggered, in milliseconds
        self.toggle_time_start = float(-1)

    # Accessor methods
    def get_relay_value(self): return self.relay_value
    def get_relay_pin(self): return self.pin_relay
    def get_sensor_pin(self): return self.pin_sensor
    def get_name(self): return self.name
    def get_sensor_value(self): return self.sensor_value
    def get_reboot_enabled(self): return self.reboot_enabled
    def get_toggle_time(self): return self.toggle_time_milliseconds
    def get_toggle_enabled(self): return self.toggle_enabled
    def get_toggle_time_start_milliseconds(self): return self.toggle_time_start

    # Modifier methods
    def set_name(self, name): self.name = name
    def set_relay_value(self, relay_value): self.relay_value = relay_value
    def set_relay_pin(self, pin): self.pin_relay = pin
    def set_sensor_pin(self, pin): self.pin_sensor = pin
    def set_sensor_value(self, sensor_value): self.sensor_value = sensor_value
    def set_reboot(self, mode): self.reboot_enabled = mode
    def set_toggle_time(
        self, toggle_time_milliseconds): self.toggle_time_milliseconds = toggle_time_milliseconds

    def set_toggle(self, toggle_enabled): self.toggle_enabled = toggle_enabled

    def set_toggle_time_start_milliseconds(
        self, toggle_time_start): self.toggle_time_start = toggle_time_start
