from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

# when the last window is closed the application closes
# Slots is the name Qt uses for the receivers of signals. In python any function or method can be
# used as a slot
class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        #self.button_is_checked = True   # need to add this line so that MainWindow class has this attribute
        self.setWindowTitle("My awesome app")

        self.button = QPushButton('This is a button')
        self.setCentralWidget(self.button)
        #self.button.setCheckable(True)
        #self.button.clicked.connect(self.the_button_was_clicked)
        #self.button.clicked.connect(self.the_button_was_toggled)     #connects the defined function to the button being clicked
        #self.button.released.connect(self.the_button_was_released)
        #self.button.setChecked(self.button_is_checked)
        #self.setFixedSize(QSize(400,300))
        self.button.clicked.connect(self.the_button_is_off)

    def the_button_was_clicked(self):
        print('clicked')

    def the_button_was_toggled(self,checked):
        print('Checked?', checked)

    def the_button_was_released(self):      #stores the state of the button (is.checked gets the state of the button)
        self.button_is_checked = self.button.isChecked()
        print(self.button_is_checked)

    def the_button_is_off(self):        #for changing the interface
        self.button.setText("You already clicked me.")
        self.button.setEnabled(False)    #makes the button unclickable
        self.setWindowTitle('Button has been clicked')
        print('The button has been clicked')


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()