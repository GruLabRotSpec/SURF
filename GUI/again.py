from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QApplication
import sys


class valonInput(QWidget):
    def __init__(self, title="", parent=None):
        super(valonInput, self).__init__(parent)
        self.title = title
        self.valonControl()

    def valonControl(self):
        layout = QVBoxLayout()

       # self.label = QLabel("Custom Parameter:")
       # layout.addWidget(self.label)

        self.input = QLabel(self.title)
        layout.addWidget(self.input)

        self.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = valonInput("Initial Value")
    widget.show()
    sys.exit(app.exec_())