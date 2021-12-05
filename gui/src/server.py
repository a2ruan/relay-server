# GUI Libraries 
import sys
import time
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtCore

# Threading Libraries
import threading
from urllib3.exceptions import NewConnectionError

# VPN and IP Libraries
import requests
from requests import *
from requests.models import Response
from requests.exceptions import ConnectionError
import socket
import ipaddress

# Global Variables
window_width = 1400
window_height = 620

# This class is the main window for the GUI
class Widget(QMainWindow):
    #Constructor
    def __init__(self, app, parent=None):
        super().__init__()

        self.app = app 
        self.relay_status = {} # Dictionary containing state of the Raspberry Pi 4
        self.init_gui(window_width,window_height)
        self.tab_group = TabGroup(self)
        self.setCentralWidget(self.tab_group)

    def keyPressEvent(self, event): # Exit when user presses ESC
        if event.key() == Qt.Key_Escape: 
            self.close()

    def init_gui(self, width, height): # Initialize GUI with specified width and height (px)
        self.setWindowIcon(QIcon('images/amd-logo-black.png')) # Set favicon
        self.setWindowTitle("AMD Relay | Version Date 11.23.2021")
        # Get screen size to center the application
        self.screen = self.app.primaryScreen()
        self.size = self.screen.size()
        self.resize(width, height)
        widget_size = self.frameGeometry()
        # Move window to the center of the screen
        self.move(int((self.size.width() - widget_size.width())/2), int((self.size.height()-widget_size.height())/2))

class TabGroup(QWidget):
    # This class is the tabs widget that populates the main window.  This contains all the different tabs/pages.

    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        # Initialize tab elements such as buttons, text ect.
        self.init_tab()

        self.headers = ['IP Address','Port Number','Host Name','Open','Delete']
        self.data = [ # default
            ["10.6.131.127", "5000", "syscomp-rpi-1.amd.com"]
        ]

        # Main Contents, Table layout
        # Row 1
        self.tab_devices.layout.addWidget(self.label_ip_address,0,0)
        self.tab_devices.layout.addWidget(self.field_ip_address,0,1)
        self.tab_devices.layout.addWidget(self.label_port_number,0,2)
        self.tab_devices.layout.addWidget(self.field_port_number,0,3)
        self.tab_devices.layout.addWidget(self.label_host_name,0,4)
        self.tab_devices.layout.addWidget(self.field_host_name,0,5)
        # Row 2
        self.tab_devices.layout.addWidget(self.btn_add_device,1,0,1,1)
        # Row 3
        self.table_widget = QTableWidget(self)
        self.init_table()
        self.tab_devices.layout.addWidget(self.table_widget,2,0,2,6)

    def init_tab(self):
        # Tab Structure
        self.tabs = QTabWidget(self)
        self.tab_devices = QWidget(self)
        self.tabs.addTab(self.tab_devices,"Devices List")

        # Add tabs to widget
        self.layout_primary = QVBoxLayout(self)
        self.layout_primary.addWidget(self.tabs)
        self.setLayout(self.layout_primary)

        # Enable close buttons on all but first tab
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        default_side = self.tabs.style().styleHint(QStyle.SH_TabBar_CloseButtonPosition, None, self.tabs.tabBar())
        self.tabs.tabBar().setTabButton(0, default_side, None)

        ## Tab 1: Devices List Tab Structure
        self.tab_devices.layout = QGridLayout(self)
        self.tab_devices.setLayout(self.tab_devices.layout)

        # QLineEdit fields
        self.field_ip_address = QLineEdit(self)
        self.field_port_number = QLineEdit(self)
        self.field_port_number.setText("5000")
        self.field_host_name = QLineEdit(self)
        self.field_host_name.setText("Automatic Detection")
        self.field_host_name.setEnabled(False)

        # QLabel labels
        self.label_ip_address = QLabel(self)
        self.label_ip_address.setText("IP Address:")
        self.label_port_number = QLabel(self)
        self.label_port_number.setText("Port Number:")
        self.label_host_name = QLabel(self)
        self.label_host_name.setText("Host Name:")
        
        # Buttons
        self.btn_add_device = QPushButton(self)
        self.btn_add_device.setText("Add to List")
        self.btn_add_device.clicked.connect(self.add_device)
        
    def init_table(self):
        # Table general appearance settings
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)    
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setFocusPolicy(Qt.NoFocus);  
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers) # MAKE CELLS READ ONLY

        # Row count
        self.table_widget.setRowCount(len(self.data)) 
        self.column_count = 5
        self.table_widget.setColumnCount(self.column_count)  
        self.table_widget.setStyleSheet("selection-background-color: #ECECEC; selection-color: #000000;");
        
        # Initialize table header
        for i, header in enumerate(self.headers):
            header_text = QTableWidgetItem()
            header_text.setText(header)
            self.table_widget.setHorizontalHeaderItem(i,header_text)

        # Populate table data and buttons
        for i, row in enumerate(self.data):
            for j, value in enumerate(row): self.table_widget.setItem(i,j, QTableWidgetItem(value))
        for row in range(len(self.data)): self.add_button(row,self.column_count-2,"Open", self.open_device)
        for row in range(len(self.data)): self.add_button(row,self.column_count-1,"Delete", self.delete_row)
        
        # Set table to auto-size to window width
        headerView = QHeaderView(QtCore.Qt.Horizontal, self.table_widget)
        self.table_widget.setHorizontalHeader(headerView)
        headerView.setSectionResizeMode(2, QHeaderView.Stretch)
        headerView.setSectionsClickable(True)

    def delete_row(self):
        # Deletes a row based on currently selected row on table
        index=(self.table_widget.selectionModel().currentIndex())
        self.data.pop(index.row())
        self.table_widget.removeRow(index.row())

    def add_device(self):
        ip = self.field_ip_address.text()
        port = self.field_port_number.text()

        if check_port(ip,int(port)): # Check if port and ip is open
            host_name = self.field_host_name.text()
            try: # Set host name via auto-detection
                host_name = socket.gethostbyaddr(ip)[0]
            except: # Set host name via text entry
                host_name = self.field_host_name.text()

            self.data.append([ip,port,host_name])
            self.table_widget.setRowCount(len(self.data)) 

            for i, row in enumerate(self.data):
                    for j, value in enumerate(row): 
                        self.table_widget.setItem(i,j, QTableWidgetItem(value))
            self.add_button(len(self.data)-1,self.column_count-2,"Open", self.open_device)
            self.add_button(len(self.data)-1,self.column_count-1,"Delete", self.delete_row)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Notification")
            msg.setText("This IP & port is invalid")
            temp_placeholder = msg.exec_()

    def add_button(self,row,column,text, target):
        btn_delete = QPushButton()
        btn_delete.setText(text)
        btn_delete.clicked.connect(target)
        btn_delete.setFont(QFont('Calibri',10))
        self.table_widget.setCellWidget(row, column, btn_delete)

    def open_device(self):
        index=(self.table_widget.selectionModel().currentIndex())
        if check_port(self.data[index.row()][0],int(self.data[index.row()][1])):
            device_tab = DeviceTab(self.tabs,index.row(), self.data)
            self.tabs.addTab(device_tab,self.data[index.row()][0] + ":" + self.data[index.row()][1])
            self.tabs.setCurrentWidget(device_tab)
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Notification")
            msg.setText("This IP & port is not online")
            temp_placeholder = msg.exec_()


class DeviceTab(QTabWidget):
    # This class creates new tabs for controlling the relay board via REST API calls

    def __init__(self,tabs,row, data):
        super(DeviceTab, self).__init__()

        self.headers = ['Relay Group', 'Relay Status','Close','Open', 'Toggle','Auto Mode','Toggle Time','Computer Status','Description']
        self.relay_state = []
        for i in range(12):
            self.relay_state.append([str(i),"Open","","","","",100,"Offline","Description"])
        
        # Create new tab and append to existing tab group
        self.ip = data[row][0]
        self.port = data[row][1]
        self.host_name = data[row][2]
        self._init_template()

    def set_relay_state(self, relay_state):
        if sorted(self.relay_state) == sorted(relay_state):
            pass
        else:
            self.relay_state = relay_state
            time.sleep(0.1)
            self.update_values()
            
    def _init_template(self):
        # Editable Fields
        self.field_ip_address = QLineEdit(self)
        self.field_ip_address.setText(self.ip)
        self.field_ip_address.setEnabled(False)

        self.field_port_number = QLineEdit(self)
        self.field_port_number.setText(self.port)
        self.field_port_number.setEnabled(False)

        self.field_host_name = QLineEdit(self)
        self.field_host_name.setText(self.host_name)
        self.field_host_name.setEnabled(False)

        # Display labels
        self.label_ip_address = QLabel(self)
        self.label_ip_address.setText("IP Address:")

        self.label_port_number = QLabel(self)
        self.label_port_number.setText("Port Number:")
        self.label_host_name = QLabel(self)
        self.label_host_name.setText("Host Name:")

        # Buttons
        self.btn_refresh = QPushButton(self)
        self.btn_refresh.setText("Refresh")
        self.btn_refresh.clicked.connect(self.update_values)

        # Layout Structure as Grid View
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

         # Row 1
        self.layout.addWidget(self.label_ip_address,0,0)
        self.layout.addWidget(self.field_ip_address,0,1)
        self.layout.addWidget(self.label_port_number,0,2)
        self.layout.addWidget(self.field_port_number,0,3)
        self.layout.addWidget(self.label_host_name,0,4)
        self.layout.addWidget(self.field_host_name,0,5)
        # Row 2
        self.layout.addWidget(self.btn_refresh,1,0)
        # Row 3
        self.table_widget = QTableWidget(self)
        self.init_relay_table()
        self.table_widget.selectRow(0) # Default select first row

    def init_relay_table(self):
        self.table_widget.verticalHeader().setVisible(False)  
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setFocusPolicy(Qt.NoFocus);  
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers) # Cells are read only
        # Initializing rows
        self.table_widget.setRowCount(len(self.relay_state)) 
        self._COLUMN_COUNT = 9
        self.table_widget.setColumnCount(self._COLUMN_COUNT)  
        self.table_widget.setStyleSheet("selection-background-color: #ECECEC;selection-color: #000000;");
        # Initializing data in table
        for _i, _header in enumerate(self.headers):
            _header_text = QTableWidgetItem()
            _header_text.setText(_header)
            self.table_widget.setHorizontalHeaderItem(_i,_header_text)
        for _i, _row in enumerate(self.relay_state):
            for _j, _value in enumerate(_row): self.table_widget.setItem(_i,_j, QTableWidgetItem(_value))
        # Adding buttons
        for _row in range(len(self.relay_state)): self.add_button(_row,self._COLUMN_COUNT-7,"Close", self.close)
        for _row in range(len(self.relay_state)): self.add_button(_row,self._COLUMN_COUNT-6,"Open", self.open)
        for _row in range(len(self.relay_state)): self.add_button(_row,self._COLUMN_COUNT-5,"Toggle", self.toggle)
        row_counter = 0
        for _row in range(len(self.relay_state)): 
            self.add_button(_row,self._COLUMN_COUNT-4,self.relay_state[row_counter][5], self.toggle_auto)
            row_counter += 1
        headerView = QHeaderView(QtCore.Qt.Horizontal, self.table_widget)
        self.table_widget.setHorizontalHeader(headerView)
        headerView.setSectionResizeMode(8, QHeaderView.Stretch)
        headerView.setSectionsClickable(False)
        self.layout.addWidget(self.table_widget,2,0,2,6)

    def add_button(self,row,column,text, target):
        btn_delete = QPushButton(self)
        btn_delete.setText(text)
        btn_delete.clicked.connect(target)
        btn_delete.setFont(QFont('Calibri',10))
        self.table_widget.setCellWidget(row, column, btn_delete)

    def update_values(self):
        print("-------------UPDATING")
        for _i, _row in enumerate(self.relay_state):
            for _j, _value in enumerate(_row): 
                #print("row=" + str(_i) + ": col=" + str(_j))
                cell_widget = self.table_widget.cellWidget(_i,_j)
                if cell_widget == None: # Filters out QPushButtons
                    placeholder_text = QTableWidgetItem(str(_value))
                    self.table_widget.setItem(_i,_j, placeholder_text)
                    if _j == 1 and _value == "Close":
                        placeholder_text.setBackground(QColor(80, 200, 120))
                    elif _j == 1 and _value == "Open":
                        placeholder_text.setBackground(QColor(255, 128, 128))
                    elif _j == 7 and _value == "Online":
                        placeholder_text.setBackground(QColor(80, 200, 120))
                    elif _j == 7 and _value == "Offline":
                        placeholder_text.setBackground(QColor(255, 128, 128))
                
        for row in range(len(self.relay_state)):
            auto_state = self.relay_state[row][5] + ""
            auto_btn_temp = self.table_widget.cellWidget(row,5)
            auto_btn_temp.setText(auto_state)
            time.sleep(0.01)
        self.table_widget.viewport().update()

    ## Rest API methods ##
    def rest_call(self, endpoint): 
        if check_port(self.ip,int(self.port)):
            print("IP&Port is okay")
            call = "http://" + self.ip + ":" + self.port + "/" + endpoint
            print(call)
            requests.get(call, timeout=2)
    
    def toggle(self): # Toggles the power button on/off
        index=(self.table_widget.selectionModel().currentIndex())
        relay_group_number = self.relay_state[index.row()][0]
        self.rest_call(str(relay_group_number) + "/toggle")

    def close(self): # Closes the relay wire, turning it on
        index=(self.table_widget.selectionModel().currentIndex())
        relay_group_number = self.relay_state[index.row()][0]
        self.rest_call(str(relay_group_number) + "/close")

    def open(self): # Opens the relay wire, turning it off
        index=(self.table_widget.selectionModel().currentIndex())
        relay_group_number = self.relay_state[index.row()][0]
        self.rest_call(str(relay_group_number) + "/open")

    def toggle_auto(self): # Auto mode triggers auto while computer is off
        index=(self.table_widget.selectionModel().currentIndex())
        relay_group_number = self.relay_state[index.row()][0]
        auto_btn = self.table_widget.cellWidget(index.row(),5)
        if auto_btn.text() == "On":
            auto_btn.setText("Off")
            self.rest_call(str(relay_group_number) + "/auto=off")
        else:
            auto_btn.setText("On")
            self.rest_call(str(relay_group_number) + "/auto=on")
        
def rest_server():
    # Gets a dictionary containing the state of the Raspberry Pi 4 using REST API.
    CLOCK_RATE_SECONDS = 0.05
    #BASE_URL = "http://10.6.131.127:5000/"
    while True:
        print("Current Tab:")
        print(widget.tab_group.tabs.currentIndex())
        tab_index = widget.tab_group.tabs.currentIndex()
        current_tab = widget.tab_group.tabs.currentWidget()

        if tab_index > 0: # Do not update dictionary if on first tab
            _ip = current_tab.ip
            _port = current_tab.port
            url = "http://" + _ip + ":" + str(_port) + "/"
            print(url)
            if check_port(_ip,int(_port)):
                print("_______________________________")
                response = requests.get(url + "status-dict")
                relay_status = response.json()
                state_list = status_dict_to_list(relay_status)
                try:
                    if tab_index > 0:
                        current_tab.set_relay_state(state_list)
                        time.sleep(0.05)
                except:
                    print("EXCEPTION OCCURRED")
                    time.sleep(1)
            else:
                print("No connection")
                no_connection_text = ["Host Offline", "NA", "NA",'NA','NA','NA','NA','NA','NA']
                connection_lost = []
                for i in range(12):
                    connection_lost.append(no_connection_text)
                if tab_index > 0:
                    current_tab.set_relay_state(connection_lost)
            time.sleep(CLOCK_RATE_SECONDS)
        else: time.sleep(CLOCK_RATE_SECONDS*10) 

def check_port(ip, port):
    # Checks if the port is open
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        socket.setdefaulttimeout(5.0) # seconds (float)
        result = sock.connect_ex((ip,port))
        sock.close()
        if result == 0: return True
        else: return False
    except:
        return False

def status_dict_to_list(status_dict):
    # Converts the returned dictionary from the REST API into a List.  This List is then used to update the status table.
    relay_state_updated = []
    for key in status_dict:
        data = status_dict[key]
        relay_group = data['PRIMARY_KEY']
        relay_value = data['RELAY_VALUE']
        relay_status = "Open"
        toggle_time = data['TOGGLE_TIME_MILLIS']
        auto_reboot_enabled = data['AUTO_REBOOT']
        auto_mode = "Off"
        sensor_value = data['SENSOR_VALUE']
        description = data['DESCRIPTION']
        computer_status = 'Offline'

        if sensor_value == 1: computer_status = 'Online'
        if auto_reboot_enabled: auto_mode = "On"
        if relay_value: relay_status = "Close"

        relay_state_row = [relay_group, relay_status, ' ',' ',' ',auto_mode,toggle_time,computer_status,description]
        relay_state_updated.append(relay_state_row)
        #print(relay_state_row)
    return relay_state_updated

class ServerThread(QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self)

    def start_server(self):
        for i in range(1,6):
            time.sleep(1)
            self.emit(QtCore.SIGNAL("dosomething(QString)"), str(i))
    def run(self):
        self.start_server()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Widget(app)
    #server = threading.Thread(target=rest_server,args=(widget,))
    server = threading.Thread(target=rest_server)
    server.name = "RESTThread"
    server.setDaemon(True)
    server.start()
    widget.show()
    app.exec_()
    sys.exit()
   