from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

# when the last window is closed the application closes, good for temporary windows

class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        self.setWindowTitle("My app")
        self.button = QPushButton('push for window')
        self.button.clicked.connect(self.show_new_window)
        self.setCentralWidget(self.button)

    def show_new_window(self, checked):
        self.w = AnotherWindow()        # IMPORTANT: keep self in front otherwise the window will disappear immediately
        self.w.show()


class AnotherWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel('Another Window')
        layout.addWidget(self.label)
        self.setLayout(layout)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()