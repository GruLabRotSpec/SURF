from PySide6.QtWidgets import QWidget, QVBoxLayout


from settings import Settings


class AdvancedSettingsPanel(QWidget):
    def __init__(self, settings: Settings):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)
