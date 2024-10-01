from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys


class ValonInput(QWidget):
    def __init__(self, title='', parent=None):
        super(ValonInput, self).__init__(parent=None)
        self.ValonInputWidgets(title)

    def ValonInputWidgets(self, title):
        layout = QHBoxLayout(self)
        Label = QLabel(title)
        Input = QDoubleSpinBox()
        Display = QLabel()
        self.Input.valueChanged['QString'].connect(self.Display.setText)
        layout.addWidget(Label)
        layout.addWidget(Input)
        layout.addWidget(Display)

    def RFLeveCreate(self):
        layout = QHBoxLayout()
        Label = QLabel(self.title)
        switch = QComboBox()
        switch.addItem('On')
        switch.addItem('Off')






class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Cavity FTMW Setup')
        self.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
        layoutMain = QGridLayout()
        ValonLayout = QVBoxLayout()

        ValonLayout.addWidget(ValonInput('Valon Frequency'))
        ValonLayout.addWidget(ValonInput('Step Frequency'))
        ValonLayout.addWidget(ValonInput('RF Level'))

        layoutMain.addLayout(ValonLayout, 1, 2)

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