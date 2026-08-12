from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout,
    QFormLayout,
    QGroupBox, 
    QCheckBox
)


from settings import Settings


class AdvancedSettingsPanel(QWidget):
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings

        layout = QVBoxLayout()
        self.setLayout(layout)

        analysis_group = QGroupBox("Analysis")

        analysis_form = QFormLayout()
        analysis_group.setLayout(analysis_form)

        self.show_points_toggle = QCheckBox("Show points on graph")
        self.show_points_toggle.setChecked(bool(settings.analysis.show_points))
        analysis_form.addRow(self.show_points_toggle)

        layout.addWidget(analysis_group)

    def update_settings(self):
        self.settings.analysis.show_points = self.show_points_toggle.isChecked()
