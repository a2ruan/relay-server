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
from requests.models import Response
headers = ['IP Address','Port Number','Host Name','Open','Delete']
data = [
    ["10.6.131.127", "5000", "SYSC-PI-1"],
    ["10.6.131.227", "5000", "SYSC-PI-2"],
    ["10.6.193.127", "5000", "SYSC-PI-3"],
    ["10.6.131.137", "5000", "SYSC-PI-4"],
    ["10.6.131.123", "5000", "SYSC-PI-5"],
    ["10.6.131.138", "5000", "SYSC-PI-6"],
    ["10.6.131.138", "5000", "SYSC-PI-7"],
    ["10.6.131.18", "5000", "SYSC-PI-8"],
    ["10.6.131.128", "5000", "SYSC-PI-9"],
    ["10.6.131.178", "5000", "SYSC-PI-10"],
    ["10.6.131.198", "5000", "SYSC-PI-11"],
    ["10.6.131.138", "5000", "SYSC-PI-12"],
    ["10.6.131.158", "5000", "SYSC-PI-13"],
    ["10.6.131.138", "5000", "SYSC-PI-14"],
    ["10.6.131.128", "5000", "SYSC-PI-15"],
    ["10.6.131.198", "5000", "SYSC-PI-16"],
    ["10.6.131.100", "5000", "SYSC-PI-17"]
]

# This class is the main window for the GUI
class Widget(QMainWindow):
    #Global constants
    WINDOW_WIDTH = 1300
    WINDOW_HEIGHT = 600

    #Constructor
    def __init__(self, app, parent=None):
        # Set up threading protocol for ascynchronous communication w/ Controller.
        # Input of constructor is a pointer to (self), to access all instance variables
        
        # Initialize Application
        super().__init__()
        #super(Widget,self).__init__(parent)
        self.app = app 
        self.relay_status = {} # Dictionary containing state of the Raspberry Pi 4
        self.init_gui(self.WINDOW_WIDTH,self.WINDOW_HEIGHT)
        self.table_widget = TabGroup(self)
        self.setCentralWidget(self.table_widget)

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
        _widget_size = self.frameGeometry()
        #Recenter GUI based on screen size and widget size
        self.move(int((self.size.width() - _widget_size.width())/2), \
            int((self.size.height()-_widget_size.height())/2))


# This class is the tabs widget that populates the main window.  This contains all the different tabs/pages.
class TabGroup(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        # Tab Structure
        self.tabs = QTabWidget(self)
        self.tab_devices = QWidget(self)
        self.tabs.addTab(self.tab_devices,"Devices List")
        #self.tab_device_utility.setDisabled(True)

        self.single_tabs = []
    
        # Add tabs to widget
        self.layout_primary = QVBoxLayout(self)
        self.layout_primary.addWidget(self.tabs)
        self.setLayout(self.layout_primary)
        
        # Enable close buttons on all but first
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        default_side = self.tabs.style().styleHint(QStyle.SH_TabBar_CloseButtonPosition, None, self.tabs.tabBar())
        self.tabs.tabBar().setTabButton(0, default_side, None)

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
        self.btn_add_device = QPushButton()
        self.btn_add_device.setText("Add to List")
        self.btn_add_device.clicked.connect(self.add_device)

        ## Tab 1: Devices List Tab Structure
        self.tab_devices.layout = QGridLayout(self)
        self.tab_devices.setLayout(self.tab_devices.layout)
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
        self._update_table()
        
    def _update_table(self):
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
            self.table_widget.setStyleSheet("selection-background-color: #ECECEC; \
            selection-color: #000000;");

            for i, header in enumerate(headers):
                header_text = QTableWidgetItem()
                header_text.setText(header)
                self.table_widget.setHorizontalHeaderItem(i,header_text)
            for i, row in enumerate(data):
                for j, value in enumerate(row): self.table_widget.setItem(i,j, QTableWidgetItem(value))
            for row in range(len(data)): self.add_button(row,self.column_count-2,"Open", self.open_device)
            for row in range(len(data)): self.add_button(row,self.column_count-1,"Delete", self.delete_row)
            
            headerView = QHeaderView(QtCore.Qt.Horizontal, self.table_widget)
            self.table_widget.setHorizontalHeader(headerView)
            headerView.setSectionResizeMode(2, QHeaderView.Stretch)
            #headerView.setSectionsClickable(True)

            self.table_widget.setColumnWidth(self.column_count-2, 60);
            self.table_widget.setColumnWidth(self.column_count-1, 60);

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
        host_name = self.field_host_name.text()
        print("Adding device")
        data.append([ip,port,host_name])
        self.table_widget.setRowCount(len(data)) 
        for i, row in enumerate(data):
                for j, value in enumerate(row): 
                    self.table_widget.setItem(i,j, QTableWidgetItem(value))
        self.add_button(len(data)-1,self.column_count-2,"Open", self.open_device)
        self.add_button(len(data)-1,self.column_count-1,"Delete", self.delete_row)

    def add_button(self,row,column,text, target):
        btn_delete = QPushButton(self)
        btn_delete.setText(text)
        btn_delete.clicked.connect(target)
        btn_delete.setFont(QFont('Calibri',10))
        #btn_delete.setStyleSheet("background-color : #FF605C")
        self.table_widget.setCellWidget(row, column, btn_delete)
    
    def open_device(self):
        print("Opening tab")
        index=(self.table_widget.selectionModel().currentIndex())
        print(index.row()) # note: the row is index starting from 0
        device_tab = DeviceTab(self.tabs,index.row())
        self.tabs.addTab(device_tab,"test")
        self.tabs.setCurrentWidget(device_tab)

class DeviceTab(QTabWidget):
    def __init__(self,tabs,row):
        #super().__init__()
        super(DeviceTab, self).__init__()

        self._headers = ['Relay Group', 'Relay Status','Close','Open', 'Toggle','Auto Mode','Toggle Time','Computer Status','Description']
        self._relay_state = [
            ["1", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["2", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["3", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["4", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["5", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["6", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["7", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["8", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["9", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["10", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["11", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description'],
            ["12", "Open", "Close",'Open','Toggle','OFF','100','ONLINE','Description']
        ]

        # Create new tab and append to existing tab group
        #self._tabs = tabs
        self._ip = data[row][0]
        self._port = data[row][1]
        self._host_name = data[row][2]

        #self._tab = QTabWidget(self)
        #self._tabs.addTab(self._tab,self._ip + ":" + self._port + str(time.time()))
        #self._tabs.setCurrentWidget(self._tab)

        #self._tab = QTabWidget(self)
        #self._tabs.addTab(self._tab,self._ip + ":" + self._port + str(time.time()))
        #self._tabs.setCurrentWidget(self._tab)
        self._init_template()
        
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
        self._tableWidget = QTableWidget(self)
        self._update_relay_table()

    def _update_relay_table(self):
        print("A")
        #self._tableWidget.verticalHeader().setVisible(False)
        #self._tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)    
        #self._tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        #self._tableWidget.setFocusPolicy(Qt.NoFocus);  
        #self._tableWidget.setEditTriggers(QTableWidget.NoEditTriggers) # MAKE CELLS READ ONLY
        print("B")
        #Row count
        self._tableWidget.setRowCount(len(self._relay_state)) 
        self._COLUMN_COUNT = 9
        self._tableWidget.setColumnCount(self._COLUMN_COUNT)  
        print("C")
        # STYLING
        self._tableWidget.setStyleSheet("selection-background-color: #ECECEC; \
        selection-color: #000000;");
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
        for _row in range(len(self._relay_state)): self._add_button(_row,self._COLUMN_COUNT-4,"ON", self.toggle_auto1)
        print("F")
        self._headerView = QHeaderView(QtCore.Qt.Horizontal, self._tableWidget)
        self._tableWidget.setHorizontalHeader(self._headerView)
        self._headerView.setSectionResizeMode(len(self._headers), QHeaderView.Stretch) # SET LAST SECTION TO STRETCH
        self._headerView.setSectionsClickable(True)
        print("G")
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-7, 60);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-6, 60);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-5, 60);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-4, 60);
        print("H")
        self.layout.addWidget(self._tableWidget,1,0,1,6)

    def _add_button(self,row,column,text, target):
        _btn_delete = QPushButton(self)
        _btn_delete.setText(text)
        _btn_delete.clicked.connect(target)
        _btn_delete.setFont(QFont('Calibri',10))
        #btn_delete.setStyleSheet("background-color : #FF605C")
        self._tableWidget.setCellWidget(row, column, _btn_delete)

    def toggle1(self):
        print("toggle")

    def close1(self):
        print("close")

    def open1(self):
        print("open")

    def toggle_auto1(self):
        print("auto")

def rest_server(widget):
    '''
    Gets a dictionary containing the state of the Raspberry Pi 4 using REST API.
    '''
    CLOCK_RATE_SECONDS = 5
    BASE_URL = "http://10.6.131.127:5000/"
    while True:
        print(time.time())
        # This will return a dictionary containing the state of all the relay groups.
        response = requests.get(BASE_URL + "status-dict")
        relay_status = response.json()
        widget.relay_status = relay_status
        time.sleep(CLOCK_RATE_SECONDS) # polling frequency is 10ms

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = Widget(app)
    server = threading.Thread(target=rest_server,args=(widget,))
    server.name = "RESTThread"
    server.setDaemon(True)
    server.start()
    widget.show()
    app.exec_()
    sys.exit()
   
    
