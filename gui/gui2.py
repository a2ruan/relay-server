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
        self.set_widgets()

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
            BASE_URL = "http://10.6.131.127:5000/"
            # This will return a dictionary containing the state of all the relay groups.
            response = requests.get(BASE_URL + "status-dict")
            self.relay_status = response.json()
            for i in self.relay_status:
                print(i + ":" + str(self.relay_status[i]))
            #self.close()
    
    #Initialize widget elements
    def set_widgets(self):
        pass

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
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Devices List")
        self.tabs.addTab(self.tab3,"Tutorial")
        
        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.pushButton1 = QPushButton("PyQt5 button")
        self.tab1.layout.addWidget(self.pushButton1)
        self.tab1.setLayout(self.tab1.layout)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        
    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(), currentQTableWidgetItem.column(), currentQTableWidgetItem.text())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w1 = Widget(app)
    w1.show()
    sys.exit(app.exec_())