from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        label = QLabel("Control")

        layout = QVBoxLayout()
        layout.addWidget(label)

        self.setLayout(layout)
