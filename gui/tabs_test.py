import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QAction, QTabWidget,QVBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

class App(QMainWindow):
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

    def __init__(self):
        super().__init__()
        self.title = "AMD RELAY | Version Date 11.23.2021"
        self.setWindowTitle(self.title)
        self.set_gui_size(self.WINDOW_WIDTH,self.WINDOW_HEIGHT)
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        
        self.show()


    def set_gui_size(self, width, height):
        #Get screen size to center the application
        self.screen = self.app.primaryScreen()
        self.size = self.screen.size()
        self.resize(width, height)
        widget_size = self.frameGeometry()
        #Recenter GUI based on screen size and widget size
        self.move(int((self.size.width() - widget_size.width())/2), \
            int((self.size.height()-widget_size.height())/2))
    
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
        self.tabs.addTab(self.tab1,"Devices")
        self.tabs.addTab(self.tab2,"Relay")
        self.tabs.addTab(self.tab3,"Documentation")
        
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
    ex = App()
    sys.exit(app.exec_())