from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import ValonGUI


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Cavity FTMW Setup')
        self.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
        layoutMain = QGridLayout()
        ValonLayout = QVBoxLayout()

        ValonFrequency = ValonGUI.CreateValon()
        StepFrequency = ValonGUI.CreateValon()
        ValonLayout.addWidget(ValonFrequency.ValonWidgets('Valon Frequency'))
        ValonLayout.addWidget(StepFrequency.ValonWidgets('Step Frequency'))


        layoutMain.addLayout(ValonLayout,1,1)

        widget = QWidget()
        widget.setLayout(layoutMain)
        self.setCentralWidget(widget)


def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    run()
