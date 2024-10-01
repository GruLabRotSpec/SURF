from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class Zaber(QWidget):
    def __init__(self, title=''):
        super(Zaber,self).__init__()
        self.title = title
        Layout = QVBoxLayout()
        option1 = {'Start Pos (mm)': 1, 'End Pos (mm)': 2}
        option2 = {'Speed (mm/s)': 1}

        if title in option1:
            widget = self.DoubleSpinBox(title)



    def DoubleSpinBox(self, title):
        ValonWidget = QWidget(self)
        layout = QHBoxLayout(self)
        Label = QLabel(title)
        Input = QDoubleSpinBox(self)
        Display = QLabel(self)
        Progress = QProgressBar()
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
        ZaberLayout = QVBoxLayout()  # for now

        layoutMain.addLayout(ZaberLayout, 1, 5)
        MainWidget.setLayout(layoutMain)
        self.setCentralWidget(MainWidget)


def run():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    run()
