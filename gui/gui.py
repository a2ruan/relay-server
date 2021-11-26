#View 

#Libaries
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import time
from qt_material import apply_stylesheet 
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

class Widget(QMainWindow):
    #Global constants
    WINDOW_WIDTH = 1300
    WINDOW_HEIGHT = 600
    WINDOW_MARGIN = 130
    LINE_THICKNESS = 2
    ELEMENT_THICKNESS = 4
    BUTTON_MARGIN = 20

    #Theme constants
    FONT_SIZE = 15 #px
    PRIMARY_COLOR = "#1de9b6"
    SECONDARY_COLOR = "#1976D2"
    TERTIARY_COLOR = "#018786"
    LOSER_COLOR = "#D3D3D3"

    #Constructor
    def __init__(self, app):
        # Set up threading protocol for ascynchronous communication w/ Controller.
        # Input of constructor is a pointer to (self), to access all instance variables

        # Initialize Application
        super().__init__()

        self.relay_status = {}

        self.setWindowIcon(QIcon('images/amd-logo-black.png'))

        self.app = app
        self.set_gui_size(self.WINDOW_WIDTH,self.WINDOW_HEIGHT)
        # Format GUI
        #apply_stylesheet(self.app,theme="light_teal.xml")
        self.setWindowTitle("AMD RELAY | Version Date 11.23.2021")

        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

    def connect_and_emit_trigger(self):
        self.trigger.connect(self.handle_trigger)

    def handle_trigger(self):
        print("trigger signal recieved")

    #Trigger on mouse click
    def mousePressEvent(self, QMouseEvent):
        x_pos = QMouseEvent.pos().x()
        y_pos = QMouseEvent.pos().y()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            for i in self.relay_status:
                print(i + ":" + str(self.relay_status[i]))
            #self.close()

    #Initialize GUI with specified width and height (px)
    def set_gui_size(self, width, height):
        #Get screen size to center the application
        self.screen = self.app.primaryScreen()
        self.size = self.screen.size()
        self.resize(width, height)
        widget_size = self.frameGeometry()
        #Recenter GUI based on screen size and widget size
        self.move(int((self.size.width() - widget_size.width())/2), \
            int((self.size.height()-widget_size.height())/2))

    def update_labels(self):
    	pass

    #Paint drawing elements to GUI
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(Qt.gray)

class MyTableWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout_primary = QVBoxLayout(self)
        
        # Tab Structure
        self.tabs = QTabWidget()
        self.tab_devices = QWidget()
    
        # Add tabs to widget
        self.layout_primary.addWidget(self.tabs)
        self.setLayout(self.layout_primary)
    
        # Add tabs
        self.tabs.addTab(self.tab_devices,"Devices List")
        #self.tab_device_utility.setDisabled(True)

        # Enable close buttons on all but first
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        default_side = self.tabs.style().styleHint(QStyle.SH_TabBar_CloseButtonPosition, None, self.tabs.tabBar())
        self.tabs.tabBar().setTabButton(0, default_side, None)

        # Editable fields
        self.field_ip_address = QLineEdit(self)
        self.field_port_number = QLineEdit(self)
        self.field_port_number.setText("5000")
        self.field_host_name = QLineEdit(self)
        self.field_host_name.setText("Automatic Detection")
        self.field_host_name.setEnabled(False)

        # Display labels
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

        ### Devices List Tab Structure
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
        self.tableWidget = QTableWidget()
        self.update_table()
        
    def update_table(self):
            self.tableWidget.verticalHeader().setVisible(False)
            self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)    
            self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
            self.tableWidget.setFocusPolicy(Qt.NoFocus);  
            self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers) # MAKE CELLS READ ONLY

            #Row count
            self.tableWidget.setRowCount(len(data)) 
            self.COLUMN_COUNT = 5
            self.tableWidget.setColumnCount(self.COLUMN_COUNT)  

            # STYLING
            self.tableWidget.setStyleSheet("selection-background-color: #ECECEC; \
            selection-color: #000000;");

            for i, header in enumerate(headers):
                header_text = QTableWidgetItem()
                header_text.setText(header)
                self.tableWidget.setHorizontalHeaderItem(i,header_text)
            for i, row in enumerate(data):
                for j, value in enumerate(row): self.tableWidget.setItem(i,j, QTableWidgetItem(value))
            for row in range(len(data)): self.add_button(row,self.COLUMN_COUNT-2,"Open", self.open_device)
            for row in range(len(data)): self.add_button(row,self.COLUMN_COUNT-1,"Delete", self.delete_row)
            
            headerView = QHeaderView(QtCore.Qt.Horizontal, self.tableWidget)
            self.tableWidget.setHorizontalHeader(headerView)
            headerView.setSectionResizeMode(2, QHeaderView.Stretch)
            #headerView.setSectionsClickable(True)

            self.tableWidget.setColumnWidth(self.COLUMN_COUNT-2, 60);
            self.tableWidget.setColumnWidth(self.COLUMN_COUNT-1, 60);

            self.tab_devices.layout.addWidget(self.tableWidget,2,0,2,6)
    
    def delete_row(self):
        print("Deleting row")
        print("Opening Device")
        index=(self.tableWidget.selectionModel().currentIndex())
        print(index.row()) # note: the row is index starting from 0
        data.pop(index.row())
        self.tableWidget.removeRow(index.row())
        print(data)

    def add_device(self):
        ip = self.field_ip_address.text()
        port = self.field_port_number.text()
        host_name = self.field_host_name.text()
        print("Adding device")
        data.append([ip,port,host_name])
        self.tableWidget.setRowCount(len(data)) 
        for i, row in enumerate(data):
                for j, value in enumerate(row): 
                    self.tableWidget.setItem(i,j, QTableWidgetItem(value))
        self.add_button(len(data)-1,self.COLUMN_COUNT-2,"Open", self.open_device)
        self.add_button(len(data)-1,self.COLUMN_COUNT-1,"Delete", self.delete_row)

    def add_button(self,row,column,text, target):
        btn_delete = QPushButton()
        btn_delete.setText(text)
        btn_delete.clicked.connect(target)
        btn_delete.setFont(QFont('Calibri',10))
        #btn_delete.setStyleSheet("background-color : #FF605C")
        self.tableWidget.setCellWidget(row, column, btn_delete)
    
    def open_device(self):
        print("Opening tab")
        index=(self.tableWidget.selectionModel().currentIndex())
        print(index.row()) # note: the row is index starting from 0
        DeviceUtility(self.tabs,index.row())

class DeviceUtility(QTabWidget):
    def __init__(self,tabs,row):

        self._headers = ['Relay Group', \
        'Relay Status','Close','Open', \
        'Toggle','Auto Mode','Toggle Time','Computer Status','Description']

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
        super(QTabWidget, self).__init__()
        self.tabs = tabs
        self._ip = data[row][0]
        self._port = data[row][1]
        self._host_name = data[row][2]

        self._tab = QTabWidget()
        self.tabs.addTab(self._tab,self._ip + ":" + self._port + str(time.time()))
        self.tabs.setCurrentWidget(self._tab)

        self.init_template()
        
    def init_template(self):
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
        self._tab.layout = QGridLayout(self)
        self._tab.setLayout(self._tab.layout)

         # Row 1
        self._tab.layout.addWidget(self._label_ip_address,0,0)
        self._tab.layout.addWidget(self._field_ip_address,0,1)
        self._tab.layout.addWidget(self._label_port_number,0,2)
        self._tab.layout.addWidget(self._field_port_number,0,3)
        self._tab.layout.addWidget(self._label_host_name,0,4)
        self._tab.layout.addWidget(self._field_host_name,0,5)
        # Row 2
        self._tableWidget = QTableWidget()
        self.update_relay_table()

    def update_relay_table(self):
        self._tableWidget.verticalHeader().setVisible(False)
        self._tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)    
        self._tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self._tableWidget.setFocusPolicy(Qt.NoFocus);  
        self._tableWidget.setEditTriggers(QTableWidget.NoEditTriggers) # MAKE CELLS READ ONLY

        #Row count
        self._tableWidget.setRowCount(len(self._relay_state)) 
        self._COLUMN_COUNT = 9
        self._tableWidget.setColumnCount(self._COLUMN_COUNT)  

        # STYLING
        self._tableWidget.setStyleSheet("selection-background-color: #ECECEC; \
        selection-color: #000000;");

        for _i, _header in enumerate(self._headers):
            _header_text = QTableWidgetItem()
            _header_text.setText(_header)
            self._tableWidget.setHorizontalHeaderItem(_i,_header_text)
        for _i, _row in enumerate(self._relay_state):
            for _j, _value in enumerate(_row): self._tableWidget.setItem(_i,_j, QTableWidgetItem(_value))
        
        for _row in range(len(self._relay_state)): self._add_button(_row,self._COLUMN_COUNT-7,"Close", self.close)
        for _row in range(len(self._relay_state)): self._add_button(_row,self._COLUMN_COUNT-6,"Open", self.open)
        for _row in range(len(self._relay_state)): self._add_button(_row,self._COLUMN_COUNT-5,"Toggle", self.toggle)
        for _row in range(len(self._relay_state)): self._add_button(_row,self._COLUMN_COUNT-4,"ON", self.toggle_auto)
        
        self._headerView = QHeaderView(QtCore.Qt.Horizontal, self._tableWidget)
        self._tableWidget.setHorizontalHeader(self._headerView)
        self._headerView.setSectionResizeMode(len(self._headers), QHeaderView.Stretch) # SET LAST SECTION TO STRETCH
        self._headerView.setSectionsClickable(True)

        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-7, 60);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-6, 60);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-5, 60);
        self._tableWidget.setColumnWidth(self._COLUMN_COUNT-4, 60);

        self._tab.layout.addWidget(self._tableWidget,1,0,1,6)

    def _add_button(self,row,column,text, target):
        _btn_delete = QPushButton()
        _btn_delete.setText(text)
        _btn_delete.clicked.connect(target)
        _btn_delete.setFont(QFont('Calibri',10))
        #btn_delete.setStyleSheet("background-color : #FF605C")
        self._tableWidget.setCellWidget(row, column, _btn_delete)

    def toggle(self):
        print("toggle")

    def close(self):
        print("close")

    def open(self):
        print("toggle")

    def toggle_auto(self):
        print("toggle")


def rest_server(widget):
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
    w1 = Widget(app)
    server = threading.Thread(target=rest_server,args=(w1,))
    server.setDaemon(True)
    server.start()
    w1.show()
    app.exec_()
    sys.exit()
   
    
