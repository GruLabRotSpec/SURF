from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys


class ValonInput(QWidget):
    def __init__(self, title='', parent=None):
        global ValonLayout, layout
        super(ValonInput, self).__init__(parent=None)
        ValonWidget = QWidget()
        self.title = title
        ValonLayout = QVBoxLayout()
        layout = QHBoxLayout()
        line = self.ValonInputWidgets(title)
        ValonLayout.addLayout(line)


    def ValonInputWidgets(self, title):
        widget = QWidget()
        Label = QLabel(title)
        Input = QDoubleSpinBox(self)
        Display = QLabel()
        Input.valueChanged['QString'].connect(Display.setText)
        layout.addWidget(Label)
        layout.addWidget(Input)
        layout.addWidget(Display)
        layout.addWidget(widget)


    def RF_Output(self):
        RFlayout = QHBoxLayout()
        RFOutputLabel = QLabel('RF Output')
        RFwidget = QComboBox(self)
        RFwidget.addItem('On')
        RFwidget.addItem('Off')
        RFwidget.addItem('---')
        RFlayout.addWidget(RFOutputLabel)
        RFlayout.addWidget(RFwidget)





class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('Cavity FTMW Setup')
        self.setStyleSheet("font: 10pt \"MS Shell Dlg 2\";")
        MainWidget = QWidget()
        layoutMain = QGridLayout()
        ValonLayout = QVBoxLayout()
        #ValonInput.RF_Level(self)


        layoutMain.addWidget(ValonInput('Valon Frequency',parent=MainWidget))
        layoutMain.addWidget(ValonInput('Step Frequency', parent = MainWidget))
        layoutMain.addWidget(ValonInput('RF Level'))
        #RF = ValonInput.RF_Output(self)

        #layoutMain.addWidget(RF)
        #layoutMain.addWidget(ValonInput('RF Output'))
        layoutMain.addLayout(ValonLayout, 1, 5)

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
