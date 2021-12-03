#View 

#Libaries
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import time
from PyQt5 import QtCore

import requests
import threading
from requests import *
from requests.models import Response
from requests.exceptions import ConnectionError
from urllib3.exceptions import NewConnectionError

# Debugging VPN issue
import socket, ipaddress, threading

# Error logging
def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)
sys.excepthook = trap_exc_during_debug


headers = ['IP Address','Port Number','Host Name','Open','Delete']
data = [
    ["10.6.131.127", "5000", "SYSC-PI-1"],
    ["10.6.131.227", "5000", "SYSC-PI-2"],
    ["10.6.193.127", "5000", "SYSC-PI-3"],
    ["10.6.131.137", "5000", "SYSC-PI-4"],
    ["10.6.131.123", "5000", "SYSC-PI-5"]
]

lock_disabled = True

relay_state_global = []
widget = []
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 620

# This class is the main window for the GUI
class Widget(QMainWindow):
    #Constructor
    def __init__(self, app, parent=None):
        # Set up threading protocol for ascynchronous communication w/ Controller.
        # Input of constructor is a pointer to (self), to access all instance variables
        
        # Initialize Application
        super().__init__()
        #super(Widget,self).__init__(parent)
        self.app = app 
        self.relay_status = {} # Dictionary containing state of the Raspberry Pi 4
        self.init_gui(WINDOW_WIDTH,WINDOW_HEIGHT)
        self.tab_group = TabGroup(self)
        self.setCentralWidget(self.tab_group)

    ''' 
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            for i in self.relay_status:
                print(i + ":" + str(self.relay_status[i]))
            #self.close()
    '''

    #Initialize GUI with specified width and height (px)
    def init_gui(self, width, height):
        self.setWindowIcon(QIcon('images/amd-logo-black.png')) # Set favicon
        self.setWindowTitle("AMD RELAY | Version Date 11.23.2021")
        #Get screen size to center the application
        self.screen = self.app.primaryScreen()
        self.size = self.screen.size()
        self.resize(width, height)
        self.setFixedSize(width,height)
        _widget_size = self.frameGeometry()
        #Recenter GUI based on screen size and widget size
        self.move(int((self.size.width() - _widget_size.width())/2), \
            int((self.size.height()-_widget_size.height())/2))


# This class is the tabs widget that populates the main window.  This contains all the different tabs/pages.
class TabGroup(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        


        self.tab_switch_indicator = 1
        # Tab Structure
        self.tabs = QTabWidget(self)
        self.tab_devices = QWidget(self)
        self.tabs.addTab(self.tab_devices,"Devices List")

        # Add tabs to widget
        self.layout_primary = QVBoxLayout(self)
        self.layout_primary.addWidget(self.tabs)
        self.setLayout(self.layout_primary)
        
        # Enable close buttons on all but first
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

        # Table Layout
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
        self.update_device_table()


    def update_device_table(self):
        # Table general appearance settings
        self.table_widget.verticalHeader().setVisible(False)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)    
        self.table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_widget.setFocusPolicy(Qt.NoFocus);  
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers) # MAKE CELLS READ ONLY

        #Row count
        self.table_widget.setRowCount(len(data)) 
        self.column_count = 5
        self.table_widget.setColumnCount(self.column_count)  

        # STYLING
        self.table_widget.setStyleSheet("selection-background-color: #ECECEC; selection-color: #000000;");
        
        for i, header in enumerate(headers):
            header_text = QTableWidgetItem()
            header_text.setText(header)
            self.table_widget.setHorizontalHeaderItem(i,header_text)
    
        for i, row in enumerate(data):
            for j, value in enumerate(row): self.table_widget.setItem(i,j, QTableWidgetItem(value))
        for row in range(len(data)): self.add_button(row,self.column_count-2,"Open", self.open_device)
        for row in range(len(data)): self.add_button(row,self.column_count-1,"Delete", self.delete_row)
        
        #headerView = QHeaderView(QtCore.Qt.Horizontal, self.table_widget)
        #self.table_widget.setHorizontalHeader(headerView)
        #headerView.setSectionResizeMode(2, QHeaderView.Stretch)
        #headerView.setSectionsClickable(True)

        general_column_width = 250
        button_column_width = 80
        horizontal_margin_spacing = 75

        self.table_widget.setColumnWidth(self.column_count-5, general_column_width);
        self.table_widget.setColumnWidth(self.column_count-4, general_column_width);
        self.table_widget.setColumnWidth(self.column_count-3, WINDOW_WIDTH-horizontal_margin_spacing-2*(general_column_width+button_column_width));
        self.table_widget.setColumnWidth(self.column_count-2, button_column_width);
        self.table_widget.setColumnWidth(self.column_count-1, button_column_width);


        self.tab_devices.layout.addWidget(self.table_widget,2,0,2,6)
    
    def delete_row(self):
        print("Deleting row")
        print("Opening Device")
        index=(self.table_widget.selectionModel().currentIndex())
        print(index.row()) # note: the row is index starting from 0
        data.pop(index.row())
        self.table_widget.removeRow(index.row())
        print(data)

    def add_device(self):
        ip = self.field_ip_address.text()
        port = self.field_port_number.text()

        if check_port(ip,int(port)):
            host_name = self.field_host_name.text()
            try:
                host_name = socket.gethostbyaddr(ip)[0]
            except:
                host_name = self.field_host_name.text()
            #self.field_host_name.setText(host_name)
            print("Adding device")
            data.append([ip,port,host_name])
            self.table_widget.setRowCount(len(data)) 
            for i, row in enumerate(data):
                    for j, value in enumerate(row): 
                        self.table_widget.setItem(i,j, QTableWidgetItem(value))
            self.add_button(len(data)-1,self.column_count-2,"Open", self.open_device)
            self.add_button(len(data)-1,self.column_count-1,"Delete", self.delete_row)
        else:
            print("Host computer not online")
            msg = QMessageBox()
            msg.setWindowTitle("Notification")
            msg.setText("This IP & port is invalid")
            temp_placeholder = msg.exec_()

    def add_button(self,row,column,text, target):
        btn_delete = QPushButton()
        btn_delete.setText(text)
        btn_delete.clicked.connect(target)
        btn_delete.setFont(QFont('Calibri',10))
        #btn_delete.setStyleSheet("background-color : #FF605C")
        self.table_widget.setCellWidget(row, column, btn_delete)

    def open_device(self):
        print("Opening tab")
        global lock_disabled
        lock_disabled = False # prevent REST API calls while 1

        index=(self.table_widget.selectionModel().currentIndex())
        print(index.row()) # note: the row is index starting from 0]
        if check_port(data[index.row()][0],int(data[index.row()][1])):
            device_tab = DeviceTab(self.tabs,index.row())
            self.tabs.addTab(device_tab,data[index.row()][0] + ":" + data[index.row()][1])
            self.tabs.setCurrentWidget(device_tab)
            
            
        else:
            print("Host computer not online")
            msg = QMessageBox()
            msg.setWindowTitle("Notification")
            msg.setText("This IP & port is not online")
            temp_placeholder = msg.exec_()
        #self.tabs.setCurrentWidget(self.tab_device_utility)
        
class DeviceTab(QTabWidget):
    def __init__(self,tabs,row):
        #super().__init__()
        super(DeviceTab, self).__init__()

        self._headers = ['Relay Group', 'Relay Status','Close','Open', 'Toggle','Auto Mode','Toggle Time','Computer Status','Description']
        self._relay_state = [ # THESE ARE DEFAULT VALUES
            ["1", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["2", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["3", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["4", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["5", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["6", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["7", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["8", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["9", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["10", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["11", "Open", 'Close','Open','Toggle','On','100','Online','Description'],
            ["12", "Open", 'Close','Open','Toggle','On','100','Online','Description']
        ]

        # Create new tab and append to existing tab group
        self._ip = data[row][0]
        self._port = data[row][1]
        self._host_name = data[row][2]
        self._init_template()
        global lock_disabled
        lock_disabled = True
        print("Lock disabled")

    def set_relay_state(self, relay_state):
        if sorted(self._relay_state) == sorted(relay_state):
            pass
            print("skipping")
        else:
            self._relay_state = relay_state
            self.update_values()
            print("updating")
            

    def _init_template(self):
        # Editable Fields
        self._field_ip_address = QLineEdit(self)
        self._field_ip_address.setText(self._ip)
        self._field_ip_address.setEnabled(False)

        self._field_port_number = QLineEdit(self)
        self._field_port_number.setText(self._port)
        self._field_port_number.setEnabled(False)

        self._field_host_name = QLineEdit(self)
        self._field_host_name.setText(self._host_name)
        self._field_host_name.setEnabled(False)

        # Display labels
        self._label_ip_address = QLabel(self)
        self._label_ip_address.setText("IP Address:")

        self._label_port_number = QLabel(self)
        self._label_port_number.setText("Port Number:")

        self._label_host_name = QLabel(self)
        self._label_host_name.setText("Host Name:")

        # Buttons
        self._btn_refresh = QPushButton(self)
        self._btn_refresh.setText("Refresh")
        self._btn_refresh.clicked.connect(self.update_values)

        # Layout Structure as Grid View
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)

         # Row 1
        self.layout.addWidget(self._label_ip_address,0,0)
        self.layout.addWidget(self._field_ip_address,0,1)
        self.layout.addWidget(self._label_port_number,0,2)
        self.layout.addWidget(self._field_port_number,0,3)
        self.layout.addWidget(self._label_host_name,0,4)
        self.layout.addWidget(self._field_host_name,0,5)
        # Row 2
        self.layout.addWidget(self._btn_refresh,1,0)
        # Row 3
        self._tableWidget = QTableWidget(self)
        self._update_relay_table()
        self._tableWidget.selectRow(0) # Default select first row

    def _update_relay_table(self):
        print("A")
        self._tableWidget.verticalHeader().setVisible(False)
        #self._tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)    
        self._tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self._tableWidget.setFocusPolicy(Qt.NoFocus);  
        self._tableWidget.setEditTriggers(QTableWidget.NoEditTriggers) # MAKE CELLS READ ONLY

        print("B")
        #Row count
        self._tableWidget.setRowCount(len(self._relay_state)) 
        self._COLUMN_COUNT = 9
        self._tableWidget.setColumnCount(self._COLUMN_COUNT)  
        print("C")
        # STYLING
        self._tableWidget.setStyleSheet("selection-background-color: #ECECEC;selection-color: #000000;");
        print("D")
        for _i, _header in enumerate(self._headers):
            _header_text = QTableWidgetItem()
            _header_text.setText(_header)
            self._tableWidget.setHorizontalHeaderItem(_i,_header_text)
        for _i, _row in enumerate(self._relay_state):
            for _j, _value in enumerate(_row): self._tableWidget.setItem(_i,_j, QTableWidgetItem(_value))
 
        print("E")
        for _row in range(len(self._relay_state)): self._add_button(_row,self._COLUMN_COUNT-7,"Close", self.close1)
        for _row in range(len(self._relay_state)): self._add_button(_row,self._COLUMN_COUNT-6,"Open", self.open1)
        for _row in range(len(self._relay_state)): self._add_button(_row,self._COLUMN_COUNT-5,"Toggle", self.toggle1)
        row_counter = 0
        for _row in range(len(self._relay_state)): 
            self._add_button(_row,self._COLUMN_COUNT-4,self._relay_state[row_counter][5], self.toggle_auto1)
            row_counter += 1
        print("F")
        #self._headerView = QHeaderView(QtCore.Qt.Horizontal, self._tableWidget)
        #self._tableWidget.setHorizontalHeader(self._headerView)
        #self._headerView.setSectionResizeMode(len(self._headers), QHeaderView.Stretch) # SET LAST SECTION TO STRETCH
        #self._headerView.setSectionsClickable(True)
        print("G")

        general_column_width = 130
        name_column_width = 250
        button_column_width = 90
        horizontal_margin_spacing = 55
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-9, name_column_width);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-8, general_column_width);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-7, button_column_width);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-6, button_column_width);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-5, button_column_width);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-4, button_column_width);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-3, general_column_width);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-2, general_column_width);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-1, WINDOW_WIDTH-horizontal_margin_spacing- \
            4*button_column_width-name_column_width-3*general_column_width);

        print("H")
        self.layout.addWidget(self._tableWidget,2,0,2,6)

    def _add_button(self,row,column,text, target):
        _btn_delete = QPushButton(self)
        _btn_delete.setText(text)
        _btn_delete.clicked.connect(target)
        _btn_delete.setFont(QFont('Calibri',10))
        #btn_delete.setStyleSheet("background-color : #FF605C")
        self._tableWidget.setCellWidget(row, column, _btn_delete)

    def update_values(self):
        print("-------------UPDATING")
        global lock_disabled
        #self._relay_state = relay_state_global
        if lock_disabled:
            for _i, _row in enumerate(self._relay_state):
                for _j, _value in enumerate(_row): 
                    print("row=" + str(_i) + ": col=" + str(_j))
                    cell_widget = self._tableWidget.cellWidget(_i,_j)
                    if cell_widget == None and lock_disabled: # Filters out QPushButtons
                        placeholder_text = QTableWidgetItem(str(_value))
                        self._tableWidget.setItem(_i,_j, placeholder_text)
                        if _j == 1 and _value == "Close" and lock_disabled:
                            placeholder_text.setBackground(QColor(80, 200, 120))
                        elif _j == 1 and _value == "Open" and lock_disabled:
                            placeholder_text.setBackground(QColor(255, 128, 128))
                        elif _j == 7 and _value == "Online" and lock_disabled:
                            placeholder_text.setBackground(QColor(80, 200, 120))
                        elif _j == 7 and _value == "Offline" and lock_disabled:
                            placeholder_text.setBackground(QColor(255, 128, 128))
                    elif lock_disabled:
                        placeholder_text = QTableWidgetItem(" ")
                        self._tableWidget.setItem(_i,_j, placeholder_text)


        print("updating viewport")
        if lock_disabled:
            self._tableWidget.viewport().update()
        print("updating buttons")
        # Update auto buttons
       
        if lock_disabled: # only run if lock is disabled, so values aren't written while it is reading
            print("lock--1")
            for row in range(len(self._relay_state)):
                if lock_disabled:
                    print("lock--2")
                    auto_state = self._relay_state[row][5] + ""
                    if lock_disabled:
                        print("lock--3")
                        auto_btn_temp = self._tableWidget.cellWidget(row,5)
                        if lock_disabled:
                            print("lock--4")
                            auto_btn_temp.setText(auto_state)
                            time.sleep(0.01)
        
        #print("updating viewport")
        #self._tableWidget.viewport().update()
        
        

    def rest_call(self, endpoint):
        if check_port(self._ip,int(self._port)):
            print("IP&Port is okay")
            call = "http://" + self._ip + ":" + self._port + "/" + endpoint
            print(call)
            requests.get(call, timeout=2)
            
    def toggle1(self):
        #self.update_values()
        print("toggle")
        index=(self._tableWidget.selectionModel().currentIndex())
        relay_group_number = self._relay_state[index.row()][0]
        self.rest_call(str(relay_group_number) + "/toggle")

    def close1(self):
        #self.update_values()
        print("close")
        index=(self._tableWidget.selectionModel().currentIndex())
        relay_group_number = self._relay_state[index.row()][0]
        self.rest_call(str(relay_group_number) + "/close")

    def open1(self):
        #self.update_values()
        print("open")
        index=(self._tableWidget.selectionModel().currentIndex())
        relay_group_number = self._relay_state[index.row()][0]
        self.rest_call(str(relay_group_number) + "/open")

    def toggle_auto1(self):
        #self.update_values()
        print("auto")
        index=(self._tableWidget.selectionModel().currentIndex())
        
        relay_group_number = self._relay_state[index.row()][0]
        auto_btn = self._tableWidget.cellWidget(index.row(),5)
        if auto_btn.text() == "On":
            auto_btn.setText("Off")
            self.rest_call(str(relay_group_number) + "/auto=off")
        else:
            auto_btn.setText("On")
            self.rest_call(str(relay_group_number) + "/auto=on")
        

def rest_server():#widget):
    '''
    Gets a dictionary containing the state of the Raspberry Pi 4 using REST API.
    '''
    CLOCK_RATE_SECONDS = 0.1
    BASE_URL = "http://10.6.131.127:5000/"
    while True:
        #print(time.time())
        # This will return a dictionary containing the state of all the relay groups.
        #global relay_state_global
        print("Current Tab:")
        print(widget.tab_group.tabs.currentIndex())
        tab_index = widget.tab_group.tabs.currentIndex()
        current_tab = widget.tab_group.tabs.currentWidget()
        #REF ONLY currentIndex=self.tabWidget.currentIndex()
        #REF ONLY currentWidget=self.tabWidget.currentWidget()
        
        if check_port('10.6.131.127',5000):# and widget.tab_group.tab_switch_indicator:
            print("connecting")
            #requests.get(BASE_URL + "status-dict")
            print("connecting1")
            response = requests.get(BASE_URL + "status-dict")
            print("connecting2")
            relay_status = response.json()
            print("connecting3")
            state_list = status_dict_to_list(relay_status)
            print("connecting4")
            #relay_state_global = state_list
            try:
                if tab_index > 0:
                    global lock_disabled
                    lock_disabled = False
                    print("LOCKED")
                    print("connecting5 TAB SWITCH INDICATOR = " + str(widget.tab_group.tab_switch_indicator))
                    current_tab.set_relay_state(state_list)
                    print("connecting6")
                    print("connecting7")
                    lock_disabled = True
                    print("UNLOCKED")
                    current_tab.update_values()
            except:
                print("EXCEPTION OCCURRED")
                time.sleep(1)
                
            time.sleep(CLOCK_RATE_SECONDS)
        else:
            print("No connection")
            no_connection_text = ["Host Offline", "NA", "NA",'NA','NA','NA','NA','NA','NA']
            connection_lost = []
            for i in range(12):
                connection_lost.append(no_connection_text)
            if tab_index > 0:
                current_tab.set_relay_state(connection_lost)
                #current_tab._btn_refresh.animateClick()
                #current_tab.update_values()
            time.sleep(0.1)
         # polling frequency is 10ms

def check_port(ip, port):
    '''
    Checks if the port is open
    '''
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP
        #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        socket.setdefaulttimeout(5.0) # seconds (float)
        result = sock.connect_ex((ip,port))
        if result == 0:
            # print ("Port is open")
            return True
        else:
            # print ("Port is closed/filtered")
            return False
        sock.close()
    except:
        return False

def status_dict_to_list(status_dict):
    '''
    Converts the returned dictionary from the REST API into a List.  This List is then used to update the status table.
    '''
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
        if sensor_value == 1:
            computer_status = 'Online'
        if auto_reboot_enabled:
            auto_mode = "On"
        if relay_value:
            relay_status = "Close"

        relay_state_row = [relay_group, relay_status, 'Close','Open','Toggle',auto_mode,toggle_time,computer_status,description]
        relay_state_updated.append(relay_state_row)
        print(relay_state_row)
    return relay_state_updated
    #print(relay_state_global)

class ServerThread(QtCore.QThread):
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
   
    
