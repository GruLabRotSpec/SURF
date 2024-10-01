from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from random import choice
# when the last window is closed the application closes
window_titles = ['My app','My app','Still my app','Still my app','What on earth', 'What on earth','This is surprising','This is surprising','Something is wrong']
class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        self.setWindowTitle("My awesome app")
        self.n_times_clicked=0
        self.button = QPushButton('This is a button')
        self.setCentralWidget(self.button)
        #self.setFixedSize(QSize(400,300))
        self.button.clicked.connect(self.the_button_was_clicked)
        self.windowTitleChanged.connect(self.the_window_title_changed)

    def the_button_was_clicked(self):
        print('Clicked')
        new_window_title = choice(window_titles)
        print('Setting title: %s' % new_window_title)
        self.setWindowTitle(new_window_title)

    def the_window_title_changed(self,window_title):
        print('Window title changed: %s' % window_title)
        if window_title == 'Something is wrong':
            self.button.setDisabled(True)





app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()