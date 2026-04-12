from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QComboBox,
)

from settings import Settings
from gui.theme import apply_theme, get_themes


class GeneralSettingsPanel(QWidget):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

        layout = QVBoxLayout()
        self.setLayout(layout)

        output_group = QGroupBox("Output options")

        output_form = QFormLayout()
        output_group.setLayout(output_form)

        location_1_label = QLabel("Folder location")
        self.output_location_field = QLineEdit("", readOnly=True)
        self.output_location_field.setText(settings.output.location)
        output_location_browse = QPushButton("Browse...")
        output_form.addRow(location_1_label)
        output_form.addRow(self.output_location_field, output_location_browse)
        output_location_browse.clicked.connect(self.get_output_location)

        filename_label = QLabel("Filename")
        self.filename_field = QLineEdit("")
        self.filename_field.setText(settings.output.filename)
        output_form.addRow(filename_label, self.filename_field)

        layout.addWidget(output_group)

        logging_group = QGroupBox("Logging")

        logging_form = QFormLayout()
        logging_group.setLayout(logging_form)

        self.logging_toggle = QCheckBox("Enable logging")
        self.logging_toggle.setChecked(True if settings.logging.enabled else False)
        logging_form.addRow(self.logging_toggle)
        self.logging_toggle.stateChanged.connect(self.on_logging_toggle)

        self.logging_location_label = QLabel("Logging location")
        self.logging_location_field = QLineEdit("", readOnly=True)
        self.logging_location_field.setText(settings.logging.location)
        self.logging_location_browse = QPushButton("Browse...")
        self.logging_location_browse.setEnabled(False)
        logging_form.addRow(self.logging_location_label)
        logging_form.addRow(self.logging_location_field, self.logging_location_browse)
        self.logging_location_browse.clicked.connect(self.get_logging_location)

        layout.addWidget(logging_group)

        theme_group = QGroupBox("Theme")

        theme_form = QFormLayout()
        theme_group.setLayout(theme_form)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(get_themes())
        self.theme_combo.setCurrentText(settings.theme)
        theme_form.addRow("Theme", self.theme_combo)

        layout.addWidget(theme_group)

    def update_settings(self):
        self.settings.output.location = self.logging_location_field.text()
        self.settings.output.filename = self.filename_field.text()
        self.settings.logging.enabled = (
            True if self.logging_toggle.isChecked() else False
        )
        self.settings.logging.location = self.logging_location_field.text()
        self.settings.theme = self.theme_combo.currentText()
        apply_theme(self.settings.theme)

    def on_logging_toggle(self):
        if self.logging_toggle.isChecked():
            self.logging_location_browse.setEnabled(True)
        else:
            self.logging_location_browse.setEnabled(False)

    def get_folder_location(self, caption, dir=""):
        dialog = QFileDialog

        folder = dialog.getExistingDirectory(self, caption, dir)
        return folder

    def get_output_location(self):
        self.output_location_field.setText(
            self.get_folder_location("Select Folder for Output", "")
        )

    def get_logging_location(self):
        self.logging_location_field.setText(
            self.get_folder_location("Select Folder for Log Output", "")
        )
