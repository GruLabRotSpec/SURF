from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class CustomUi(QWidget):
    def __int__(self):
        super().__init__()
        # maybe here I should initialize instruments, if they don't work then have dialog box pop up showing the error
        self.init_ui()

    def init_ui(self, *args,**kwargs):

        MainWindow.setWindowTitle('Cavity FTMW Setup')
        MainWindow.setGeometry(100,100,1000,500)
        MainWindow.setStyleSheet('font: 10pt \"MS Shell Dlg 2\"')

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName('Central Widget')
        valonLayout = QGridLayout()

        self.ValonFrequencyLabel = QLabel('Valon Frequency')
        valonLayout.addWidget(self.ValonFrequencyLabel,0,0)
        self.ValonFrequencyInput = QDoubleSpinBox()
        valonLayout.addWidget(self.ValonFrequencyInput,1,0)

        ValonWidget = QWidget()
        ValonWidget.setLayout(valonLayout)



def run():
    app = QApplication(sys.argv)

    window = QMainWindow()
    ui = CustomUi()
    ui.init_ui(window)
    window.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    run()