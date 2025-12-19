from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton

from gui.settings_window import SettingsWindow

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        label = QLabel("Control")

        layout = QVBoxLayout()
        layout.addWidget(label)

        self.setLayout(layout)

        show_button = QPushButton("View additional settings...")
        show_button.clicked.connect(self.show_more_settings)
        layout.addWidget(show_button)

    def show_more_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()
