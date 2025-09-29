from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QProgressBar


class BottomBarPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        bottom_text = QLabel("Idle, ready to scan")
        layout.addWidget(bottom_text)

        bottom_progress_bar = QProgressBar(maximum=1, textVisible=False)
        bottom_progress_bar.setValue(1)
        layout.addWidget(bottom_progress_bar)
        layout.setStretch(1, 1)

        layout.addStretch(5)

        self.setLayout(layout)
