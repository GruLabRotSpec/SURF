from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

# when you rightclick the three options are added as clickable options
# Not quite sure about Layout forwarding
class MainWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)
        self.setWindowTitle("My awesome app")

# this is one method
    #def contextMenuEvent(self, e):  #overrides the original object method
    #    context = QMenu(self)
    #    context.addAction(QAction('test 1', self))
    #    context.addAction(QAction('test 2', self))
    #    context.addAction(QAction('test 3', self))
    #    context.exec(e.globalPos())     #when passing the initial position to the exec function, this must be relative to the parent passed in the function, but since we passed self, we can use the global position

# second method of adding a context Menu
        self.show()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_context_menu)

    def on_context_menu(self,pos):
        context = QMenu(self)
        context.addAction(QAction('test 1', self))
        context.addAction(QAction('test 2', self))
        context.addAction(QAction('test 3', self))
        context.exec(self.mapToGlobal(pos))
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()