from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

# four basic layouts
#QHBoxLAyout
#QVBoxLayout
#QGridLayout
#QStackedLayout

class Color(QWidget):
    def __init__(self, colorr):
        super(Color,self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window,QColor(colorr))
        self.setPalette(palette)

class valonInput(QWidget):
    def __init__(self, parent=None):
        super(valonInput, self).__init__(parent=None)
        layout = QGridLayout(self)
        self.setLayout(layout)
        Widget = QDoubleSpinBox()
        label = QLabel('test')
        layout.addWidget(Widget)
        layout.addWidget(label)


class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        self.setWindowTitle("My app")
        layout = QVBoxLayout()          #can replace with any of the other basic layouts and the rest of the code stays the same

        layout.addWidget(Color('red'))
        layout.addWidget(Color('blue')) #adds block to the specified layout
        #widget = Color('red')       #will just be a red block
        layout.addWidget(valonInput())

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()