from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class Valon(QWidget):
    def __init__(self, title):
        super(Valon, self).__init__()
        self.title=title
        #self.ValonWidget(title)
        Label = QLabel(title)
        layout = QHBoxLayout()
        layout.addWidget(Label)

    def ValonWidget(self):
        pass



class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        layout = QVBoxLayout()

        ValonLayout = QHBoxLayout()
        ValonFreq=Valon('hi there')


        layout.addLayout(ValonLayout)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    pass


def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    run()
