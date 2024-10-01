from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys


class Valon(QWidget):
    def __init__(self, title=''):
        super(Valon, self).__init__()
        self.title = title
        Layout = QVBoxLayout()
        option1 = {'Valon Frequency': 1, 'Step Frequency': 2, 'RF Level': 3}
        option2 = {'RF Output': 1, 'Synth Power': 2}
        if title in option1:
            widget = self.DoubleSpinBox(title)
            Layout.addLayout(widget)
        elif title in option2:
            widget = self.OnOffSwitch(title)
            Layout.addLayout(widget)


    def DoubleSpinBox(self, title):
        ValonWidget = QWidget(self)
        layout = QHBoxLayout(self)
        Label = QLabel(title)
        Input = QDoubleSpinBox(self)
        Display = QLabel(self)
        Input.valueChanged['QString'].connect(Display.setText)
        layout.addWidget(Label)
        layout.addWidget(Input)
        layout.addWidget(Display)
        layout.addWidget(ValonWidget)
        return layout

    def OnOffSwitch(self, title):
        RFlayout = QHBoxLayout(self)
        RFOutputLabel = QLabel(title)
        RFwidget = QComboBox(self)
        RFwidget.addItem('On')
        RFwidget.addItem('Off')
        RFwidget.addItem('---')
        RFlayout.addWidget(RFOutputLabel)
        RFlayout.addWidget(RFwidget)