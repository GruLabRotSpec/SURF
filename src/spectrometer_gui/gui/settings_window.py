from PySide6.QtWidgets import (
    QWidget,
    QTabWidget,
    QVBoxLayout
)

from gui.general_settings_panel import GeneralSettingsPanel
from gui.advanced_settings_panel import AdvancedSettingsPanel

class SettingsWindow(QWidget):
    def __init__(self):
        super.__init__()

        self.setWindowTitle("Settings")

        layout = QVBoxLayout()
        self.setLayout(layout)

        general_settings_panel = GeneralSettingsPanel()
        advanced_settings_panel = AdvancedSettingsPanel()

        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(general_settings_panel, "General")
        self.tab_widget.addTab(advanced_settings_panel, "Advanced")

        layout.addWidget(self.tab_widget)
