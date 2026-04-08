from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout, QPushButton

from pathlib import Path

from settings import Settings, save_settings

from gui.general_settings_panel import GeneralSettingsPanel
from gui.advanced_settings_panel import AdvancedSettingsPanel


class SettingsWindow(QWidget):
    def __init__(self, settings: Settings, settings_path: Path):
        super().__init__()

        self.settings = settings
        self.settings_path = settings_path

        self.setWindowTitle("Settings")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.general_settings_panel = GeneralSettingsPanel(settings)
        advanced_settings_panel = AdvancedSettingsPanel(settings)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(self.general_settings_panel, "General")
        self.tab_widget.addTab(advanced_settings_panel, "Advanced")

        layout.addWidget(self.tab_widget)

        self.apply_btn = QPushButton("Save and apply")
        self.apply_btn.clicked.connect(self.on_save_clicked)
        layout.addWidget(self.apply_btn)

    def on_save_clicked(self):
        self.general_settings_panel.update_settings()
        save_settings(self.settings_path, self.settings)
