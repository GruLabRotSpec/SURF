import re
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
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QHBoxLayout,
)

from settings import Settings, ScopePresetItem
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
        self.logging_toggle.setChecked(bool(settings.logging.enabled))
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

        oscilloscope_presets_group = QGroupBox("Oscilloscope Presets")

        oscilloscope_presets_layout = QVBoxLayout()
        oscilloscope_presets_group.setLayout(oscilloscope_presets_layout)

        root_path_layout = QHBoxLayout()
        root_path_label = QLabel("Root file path")
        self.preset_root_path_field = QLineEdit("")
        self.preset_root_path_field.setText(
            settings.scope_preset.root_path if settings.scope_preset else ""
        )
        root_path_layout.addWidget(root_path_label)
        root_path_layout.addWidget(self.preset_root_path_field)
        oscilloscope_presets_layout.addLayout(root_path_layout)

        self.presets_table = QTableWidget()
        self.presets_table.setColumnCount(3)
        self.presets_table.setHorizontalHeaderLabels(["Name", "File", ""])

        header = self.presets_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        oscilloscope_presets_layout.addWidget(self.presets_table)

        self.add_preset_btn = QPushButton("Add")
        self.add_preset_btn.clicked.connect(self.add_preset_row)
        oscilloscope_presets_layout.addWidget(self.add_preset_btn)

        presets = {}
        if self.settings.scope_preset and self.settings.scope_preset.presets:
            presets = self.settings.scope_preset.presets

        for _, preset in presets.items():
            self.add_preset_row(preset.name, preset.path)

        layout.addWidget(oscilloscope_presets_group)

    def add_preset_row(self, name="", path=""):
        row = self.presets_table.rowCount()
        self.presets_table.insertRow(row)
        self.presets_table.setItem(row, 0, QTableWidgetItem(name))
        self.presets_table.setItem(row, 1, QTableWidgetItem(path))

        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        remove_btn = QPushButton("X")
        remove_btn.setFixedWidth(30)
        remove_btn.clicked.connect(lambda: self.remove_preset_row(row))
        layout.addWidget(remove_btn)
        widget.setLayout(layout)
        self.presets_table.setCellWidget(row, 2, widget)

    def remove_preset_row(self, row):
        self.presets_table.removeRow(row)

    def update_settings(self):
        self.settings.output.location = self.output_location_field.text()
        self.settings.output.filename = self.filename_field.text()
        self.settings.logging.enabled = self.logging_toggle.isChecked()
        self.settings.logging.location = self.logging_location_field.text()
        self.settings.theme = self.theme_combo.currentText()
        self.settings.scope_preset.root_path = self.preset_root_path_field.text()

        presets = {}
        for row in range(self.presets_table.rowCount()):
            name_item = self.presets_table.item(row, 0)
            path_item = self.presets_table.item(row, 1)
            if name_item and path_item:
                name = name_item.text()
                path = path_item.text()
                if not name or not path:
                    continue

                # Convert to snake case
                key = re.sub(r"\s+", "_", name.lower().strip())
                presets[key] = ScopePresetItem(name=name, path=path)

        self.settings.scope_preset.presets = presets
        apply_theme(self.settings.theme)

    def on_logging_toggle(self):
        if self.logging_toggle.isChecked():
            self.logging_location_browse.setEnabled(True)
        else:
            self.logging_location_browse.setEnabled(False)

    def get_folder_location(self, caption, dir_path=""):
        dialog = QFileDialog

        folder = dialog.getExistingDirectory(self, caption, dir_path)
        return folder

    def get_output_location(self):
        self.output_location_field.setText(
            self.get_folder_location("Select Folder for Output", "")
        )

    def get_logging_location(self):
        self.logging_location_field.setText(
            self.get_folder_location("Select Folder for Log Output", "")
        )
