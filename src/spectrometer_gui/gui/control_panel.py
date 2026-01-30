from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QComboBox,
)

from gui.settings_window import SettingsWindow


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()


        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left Column
        left_column = QVBoxLayout()
        left_column_panel = QWidget()
        left_column_panel.setLayout(left_column)

        left_column.addStretch(1)

        label = QLabel("Control")
        left_column.addWidget(label)

        zaber_group = QGroupBox("Zaber")

        zaber_form = QFormLayout()
        zaber_group.setLayout(zaber_form)

        zaber_speed_1_label = QLabel("Zaber scanning speed")
        zaber_speed_1_field = QLineEdit("0.1")
        zaber_form.addRow(zaber_speed_1_label, zaber_speed_1_field)

        zaber_speed_2_label = QLabel("Zaber homing speed")
        zaber_speed_2_field = QLineEdit("2.0")
        zaber_form.addRow(zaber_speed_2_label, zaber_speed_2_field)

        left_column.addWidget(zaber_group)

        awg_group = QGroupBox("Arbitrary waveform generator")

        awg_form = QFormLayout()
        awg_group.setLayout(awg_form)

        status_label = QLabel("Status")
        on_btn = QPushButton("Run")
        off_btn = QPushButton("Stop")
        awg_form.addRow(status_label, on_btn)
        awg_form.addRow(status_label, off_btn)

        run_mode_label = QLabel("Run mode")
        run_mode_field = QComboBox()
        run_mode_field.addItems(["Continuous", "Triggered"])

        ch_1_label = QLabel("Channel 1")
        ch_1_on_btn = QPushButton("On")
        ch_1_off_btn = QPushButton("Off")
        awg_form.addRow(ch_1_label, ch_1_on_btn)
        awg_form.addRow(ch_1_label, ch_1_off_btn)

        ch_2_label = QLabel("Channel 2")
        ch_2_on_btn = QPushButton("On")
        ch_2_off_btn = QPushButton("Off")
        awg_form.addRow(ch_2_label, ch_2_on_btn)
        awg_form.addRow(ch_2_label, ch_2_off_btn)

        left_column.addWidget(awg_group)

        valon_group = QGroupBox("Valon")

        valon_form = QFormLayout()
        valon_group.setLayout(valon_form)

        rf_label = QLabel("RF level (power)")
        rf_field = QLineEdit("10")
        valon_form.addRow(rf_label, rf_field)

        layout.addWidget(valon_group)

        oscilloscope_group = QGroupBox("Oscilloscope")

        oscilloscope_form = QFormLayout()
        oscilloscope_group.setLayout(oscilloscope_form)

        resolution_label = QLabel("Resolution")
        resolution_field = QLineEdit("")
        oscilloscope_form.addRow(resolution_label, resolution_field)

        sample_rate_label = QLabel("Sample rate")
        sample_rate_field = QLineEdit("")
        oscilloscope_form.addRow(sample_rate_label, sample_rate_field)

        window_type_label = QLabel("Window type")
        window_type_field = QLineEdit()
        oscilloscope_form.addRow(window_type_label, window_type_field)

        gate_position_label = QLabel("Gate position")
        gate_position_field = QLineEdit()
        oscilloscope_form.addRow(gate_position_label, gate_position_field)

        math_avg_label = QLabel("Math averages")
        math_avg_field = QLineEdit()
        oscilloscope_form.addRow(math_avg_label, math_avg_field)

        left_column.addWidget(oscilloscope_group)

        # Right Column
        right_column = QVBoxLayout()
        right_column_panel = QWidget()
        right_column_panel.setLayout(right_column)

        right_column.addStretch(1)

        timing_group = QGroupBox("Delay generator")

        timing_form = QFormLayout()
        timing_group.setLayout(timing_form)

        delay_gas_label = QLabel("Delay gas - MW")
        delay_gas_field = QLineEdit()
        timing_form.addRow(delay_gas_label, delay_gas_field)

        right_column.addWidget(timing_group)

        layout.addWidget(left_column_panel)
        layout.addWidget(right_column_panel)

        layout.setStretch(0, 1)
        layout.setStretch(1, 1)

    def show_more_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()
