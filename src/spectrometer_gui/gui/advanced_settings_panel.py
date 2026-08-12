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

        self.show_grid_toggle = QCheckBox("Show grid on analysis graph")
        self.show_grid_toggle.setChecked(bool(settings.analysis.show_grid))
        analysis_form.addRow(self.show_grid_toggle)

        self.show_crosshair_toggle = QCheckBox("Show crosshairs on analysis graph")
        self.show_crosshair_toggle.setChecked(bool(settings.analysis.show_crosshair))
        analysis_form.addRow(self.show_crosshair_toggle)

        layout.addWidget(analysis_group)

    def update_settings(self):
        self.settings.analysis.show_points = self.show_points_toggle.isChecked()
        self.settings.analysis.show_grid = self.show_grid_toggle.isChecked()
        self.settings.analysis.show_crosshair = self.show_crosshair_toggle.isChecked()
