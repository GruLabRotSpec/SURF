from PyQt5.QtWidgets import *
import sys


class valonInput(QWidget):
    def __init__(self, title="", parent=None):
        super(valonInput, self).__init__(parent)
        test = QLabel('test text')
        self.title = title
        layout = QHBoxLayout()
        Label = QLabel(self.title)
        Input = QDoubleSpinBox()
        Input.setObjectName(self.title+'Input')
        layout.addWidget(Label)
        layout.addWidget(Input)
        layout.addWidget(test)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle('Cavity FTMWW Setup')
        layoutMain = QHBoxLayout()
        valonLayout=QVBoxLayout()
        layoutMain.addLayout(valonLayout)
        valonLayout.addWidget(valonInput('testinggg'))

        ValonWidget = QWidget()

        self.setCentralWidget(ValonWidget)
        ValonWidget.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window=MainWindow()
    valonLayout = QVBoxLayout()
    ValonFrequency = valonLayout.addWidget(valonInput('Valon Frequency'))
    ValonWidget = QWidget()
    ValonWidget.setLayout(valonLayout)
    window.setCentralWidget(ValonWidget)
    ValonWidget.show()
    window.show()

    sys.exit(app.exec_())
