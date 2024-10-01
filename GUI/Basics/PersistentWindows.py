from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from random import randint

# when the last window is closed the application closes, good for temporary windows

class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        self.w = AnotherWindow()        # Defining this here keeps it a permanent window
        self.w1 = AnotherWindow()
        self.setWindowTitle("My app")

        self.layout = QVBoxLayout()
        self.button = QPushButton('push for window')
        #self.button.clicked.connect(self.show_new_window)
        #self.button.clicked.connect(self.toggle_window)
        #self.setCentralWidget(self.button)
        self.button.clicked.connect(lambda checked: self.toggle_window(self.w))
        self.layout.addWidget(self.button)

        self.button2 = QPushButton('push for window 1')
        #self.button2.clicked.connect(self.toggle_window1)
        self.layout.addWidget(self.button2)
        self.button2.clicked.connect(lambda checked: self.toggle_window(self.w1)) # eh use other version to be sure

        w = QWidget()
        w.setLayout(self.layout)
        self.setCentralWidget(w)


    def show_new_window(self, checked):
       # IMPORTANT: keep self in front otherwise the window will disappear immediately
        self.w.show()

    def toggle_window(self, checked):       # makes visible if invisible, makes invisible if visible
        if self.w.isVisible():
            self.w.hide()
        else:
            self.w.show()


    def toggle_window1(self, checked):
            if self.w1.isVisible():
                self.w1.hide()
            else:
                self.w1.show()
class AnotherWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel('Another Window % d' % randint(0,100))
        layout.addWidget(self.label)
        self.setLayout(layout)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()