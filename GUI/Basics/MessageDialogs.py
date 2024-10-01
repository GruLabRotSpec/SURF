from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


# when the last window is closed the application closes
class CustomDialog(QDialog):
    def __init__(self,parent=None):
        super(CustomDialog, self).__init__(parent)
        self.setWindowTitle('Alert')
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel('Something happened, is that OK?')
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        self.setWindowTitle("My app")

        button = QPushButton('Press me for dialog')
        button.clicked.connect(self.button_clicked)
        self.setCentralWidget(button)

    def button_clicked(self,s):
        print('click',s)
        #dlg = QMessageBox(self)
        #dlg.setWindowTitle('I have a question')
        #dlg.setText('message dialog')
        #button = dlg.exec()

        #if button == QMessageBox.Ok:
        #    print('Ok!')
        button = QMessageBox.question(self,'question','asking the question')

        if button == QMessageBox.Yes:
            print('Yes')
        else:
            print('No')
            quit()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()