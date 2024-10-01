from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

# grid layout is what should be used here
class Color(QWidget):
    def __init__(self, color):
        super(Color,self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window,QColor(color))
        self.setPalette(palette)


class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        self.setWindowTitle("My app")
        layout = QGridLayout()

        layout.addWidget(Color('red'), 0,0)
        layout.addWidget(Color('green'),1,0)
        layout.addWidget(Color('blue'),2,3)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()