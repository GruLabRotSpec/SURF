from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

# when the last window is closed the application closes

class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        self.setWindowTitle("My app")
        label = QLabel('Hi')
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)

        toolbar = QToolBar('My main toolbar')
        self.addToolBar(toolbar)

        button_action = QAction('Your button', self)
        button_action.setStatusTip('This is your button tip')
        button_action.triggered.connect(self.onMyToolBarButtonClick)
        button_action.setCheckable(True)        # makes the button checkable
        toolbar.addAction(button_action)
        toolbar.addSeparator()      #adds a line between options, can also be used with menuBar
        toolbar.addWidget(QLabel('label'))

        self.setStatusBar(QStatusBar(self))

        menu = self.menuBar()
        file_menu = menu.addMenu('&File')
        file_menu.addAction(button_action)
        file_submenu = file_menu.addMenu('SubMenu')
        file_submenu.addAction(button_action)
    def onMyToolBarButtonClick(self,s):
        print('click',s)

# signal is always false because the signal is based on checked status and the button is not checked it is clickable

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

# you can set the toolbar to be represented by images if you want just need to download
# button_action = QAction(QIcon('bug.png'),'Your button',self)
# Qt.ToolButtonFollowStyle follows the host style by default