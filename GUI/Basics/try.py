from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QApplication
import sys


class ValonInput(QWidget):
    def __int__(self, custom_param="", parent=None):
        super(ValonInput, self).__init__(parent)
        self.custom_param = custom_param
        self.ValonControl()


    def ValonControl(self):
        layout = QVBoxLayout()

        self.label = QLabel("Custom Parameter:")
        layout.addWidget(self.label)

        self.input = QLineEdit(self.custom_param)
        layout.addWidget(self.input)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ValonInput('initial Value')
    widget.show()
    app.exec_()