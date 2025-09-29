from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class AnalysisPanel(QWidget):
    def __init__(self):
        super().__init__()

        label = QLabel("Analysis")

        layout = QVBoxLayout()
        layout.addWidget(label)

        self.setLayout(layout)
