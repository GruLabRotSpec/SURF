from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout
)

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About")

        layout = QVBoxLayout()
        self.setLayout(layout)
