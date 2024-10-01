from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

# this allows an input field and below it printed what was inputted

class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        self.setWindowTitle("My awesome app")

        self.Label = QLabel()
        self.input = QLineEdit()
        self.input.textChanged.connect(self.Label.setText)  # puts the label underneath the type input

        layout = QVBoxLayout()
        layout.addWidget(self.input)
        layout.addWidget(self.Label)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)




app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()