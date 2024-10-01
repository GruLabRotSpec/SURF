from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import ValonGUI

class Zaber(QWidget):
    def __init__(self):
        super(Zaber,self).__init__()

    def DoubleSpinBox(self, title):
        ValonWidget = QWidget(self)
        layout = QHBoxLayout(self)
        Label = QLabel(title)
        Input = QDoubleSpinBox(self)
        Display = QLabel(self)
        Input.valueChanged['QString'].connect(Display.setText)
        layout.addWidget(Label)
        layout.addWidget(Input)
        layout.addWidget(Display)
        layout.addWidget(ValonWidget)
        return layout


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Cavity FTMW Setup')
        self.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
        MainWidget = QWidget()
        layoutMain = QGridLayout()
        ValonLayout = QVBoxLayout()

        ValonLayout.addWidget(ValonGUI.Valon('Valon Frequency'))
        ValonLayout.addWidget(ValonGUI.Valon('Step Frequency'))
        ValonLayout.addWidget(ValonGUI.Valon('RF Level'))
        ValonLayout.addWidget(ValonGUI.Valon('RF Output'))
        ValonLayout.addWidget(ValonGUI.Valon('Synth Power'))

        layoutMain.addLayout(ValonLayout, 1, 5)
        MainWidget.setLayout(layoutMain)
        self.setCentralWidget(MainWidget)




def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    run()
