import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication

class basicMenubar(QMainWindow):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        
        self.initUI()        
        
    def initUI(self):    
        
        self.setGeometry(200, 200, 200, 200)           
        
        exitAction = QAction('&Exit', self)        
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        
        
        self.setWindowTitle('PyQt5 Basic Menubar')    
        self.show()
        
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = basicMenubar()
    sys.exit(app.exec_())