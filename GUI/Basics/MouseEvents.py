from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

# allows the code to respond differently depending on which button on the mouse is pressed
# .button()
# .buttons()
# .globalPos()
# .globalX()
# .globalY()
# .pos() - integer position
# .posF() - float position
# there is also Qt.NoButton()

class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        self.label=QLabel('Click this window')
        self.setCentralWidget(self.label)

    def mouseMoveEvent(self, e):
        self.label.setText('mouseMoveEvent')

    def mousePressEvent(self, e):
        #self.label.setText('mousePressEvent')
        if e.button == Qt.LeftButton:
            self.label.setText('mousePressEvent LEFT')
        elif e.button()==Qt.MiddleButton:
            self.label.setText('mousePressEvent MIDDLE')
        elif e.button()==Qt.RightButton:
            self.label.setText('mousePressEvent RIGHT')
    def mouseReleaseEvent(self, e):
        #self.label.setText('mouseReleaseEvent')
        if e.button == Qt.LeftButton:
            self.label.setText('mouseReleaseEvent LEFT')
        elif e.button()==Qt.MiddleButton:
            self.label.setText('mouseReleaseEvent MIDDLE')
        elif e.button()==Qt.RightButton:
            self.label.setText('mouseReleaseEvent RIGHT')
    def mouseDoubleClickEvent(self, e):
        #self.label.setText('mouseDoubleClickEvent')
        if e.button == Qt.LeftButton:
            self.label.setText('mouseDoubleClickEvent LEFT')
        elif e.button()==Qt.MiddleButton:
            self.label.setText('mouseDoubleClickEvent MIDDLE')
        elif e.button()==Qt.RightButton:
            self.label.setText('mouseDoubleClickEvent RIGHT')

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()