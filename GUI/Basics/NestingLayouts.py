from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

# organizing several widgets in one window however it is easier to use grid style
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
        layout1 = QHBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()

        layout2.addWidget(Color('red'))
        layout2.addWidget(Color('yellow'))
        layout2.addWidget(Color('purple'))

        layout1.addLayout(layout2)
        layout1.addWidget(Color('red'))

        layout3.addWidget(Color('green'))
        layout3.addWidget(Color('purple'))

        layout1.addLayout(layout3)
        layout1.setContentsMargins(0,0,0,0)
        layout1.setSpacing(20)
        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()