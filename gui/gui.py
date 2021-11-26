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
headers = ['IP Address','Port Number','Host Name']
data = [
    ["10.6.193.227", "5000", "SYSC-PI-1"],
    ["10.6.131.227", "5000", "SYSC-PI-2"],
    ["10.6.193.127", "5000", "SYSC-PI-3"],
    ["10.6.131.137", "5000", "SYSC-PI-4"],
    ["10.6.131.108", "5000", "SYSC-PI-5"],
]


class Widget(QMainWindow):
    #Global constants
    WINDOW_WIDTH = 1200
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
        self.tab_tutorials = QWidget()
    
        # Add tabs to widget
        self.layout_primary.addWidget(self.tabs)
        self.setLayout(self.layout_primary)
    
        # Add tabs
        self.tabs.addTab(self.tab_devices,"Devices List")
        #self.tabs.addTab(self.tab_tutorials,"Tutorial")
        
        # Editable fields
        self.field_ip_address = QLineEdit(self)
        self.field_port_number = QLineEdit(self)
        self.field_host_name = QLineEdit(self)

        # Display labels
        self.label_ip_address = QLabel(self)
        self.label_ip_address.setText("IP Address:")
        self.label_port_number = QLabel(self)
        self.label_port_number.setText("Port Number:")
        self.label_host_name = QLabel(self)
        self.label_host_name.setText("Host Name:")

        # Buttons
        self.btn_add_device = QPushButton()
        self.btn_add_device.setText("Add Device to List")

        # Device List Table
        self.device_table = QTableView() 
        self.device_table.setSelectionBehavior(QTableView.SelectRows) # Select by row
        self.device_table.verticalHeader().setVisible(False) # Hide row numbers
        self.model = TableModel(data,headers)
        self.device_table.setModel(self.model)

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
        self.header_policy = self.device_table.horizontalHeader()
        self.header_policy.setSectionResizeMode(QHeaderView.Stretch)
        self.tab_devices.layout.addWidget(self.device_table,2,0,2,6)

class TableModel(QAbstractTableModel):
    def __init__(self, data, titles):
        super(TableModel, self).__init__()
        self._data = data
        self.horizontalHeaders = titles

        for i,header in enumerate(self.horizontalHeaders):
            self.setHeaderData(i, Qt.Horizontal, header)

    def setHeaderData(self, section, orientation, data, role=Qt.EditRole):
        if orientation == Qt.Horizontal and role in (Qt.DisplayRole, Qt.EditRole):
            try:
                self.horizontalHeaders[section] = data
                return True
            except:
                return False
        return super().setHeaderData(section, orientation, data, role)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            try:
                return self.horizontalHeaders[section]
            except:
                pass
        return super().headerData(section, orientation, role)


    def data(self, index, role):
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])






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
   
    
