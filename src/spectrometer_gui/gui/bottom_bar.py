from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QProgressBar


class BottomBarPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.bottom_text = QLabel("Idle, ready to scan")
        layout.addWidget(self.bottom_text)

        self.bottom_progress_bar = QProgressBar(maximum=1, textVisible=False)
        self.bottom_progress_bar.setValue(1)
        layout.addWidget(self.bottom_progress_bar)
        layout.setStretch(1, 1)

        layout.addStretch(5)

        self.setLayout(layout)

    def set_status_elements(self, progress, text="Working"):
        if progress === -1:
            self.bottom_progress_bar.setRange(0, 0)
        else:
            self.bottom_progress_bar.setRange(0, 1)
            self.bottom_progress_bar.setValue(progress)

        self.bottom_text.setText(text)
