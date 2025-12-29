from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton

from gui.settings_window import SettingsWindow

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        label = QLabel("Control")

        layout = QVBoxLayout()
        layout.addWidget(label)

        self.setLayout(layout)

        zaber_group = QGroupBox()

        zaber_form = QFormLayout()
        zaber_group.setLayout(zaber_form)

        zaber_speed_1_label = QLabel("Zaber scanning speed")
        zaber_speed_1_field = QLineEdit("0.1")
        zaber_form.addRow(zaber_speed_1_label, zaber_speed_1_field)

        zaber_speed_2_label = QLabel("Zaber homing speed")
        zaber_speed_2_field = QLineEdit("2.0")
        zaber_form.addRow(zaber_speed_2_label, zaber_speed_2_field)

        self.addWidget(zaber_group)

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

        self.addWidget(awg_group)

        valon_group = QGroupBox()

        valon_form = QFormLayout()
        valon_group.setLayout(valon_form)

        rf_label = QLabel("RF level (power)")
        rf_field = QLineEdit("10")
        valon_form.addRow(rf_label, rf_field)

        self.addWidget(valon_group)

        oscilloscope_group = QGroupBox()

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

        self.addWidget(oscilloscope_group)

        timing_group = QGroupBox()

        timing_form = QFormLayout()
        timing_group.setLayout(timing_form)

        delay_gas_label = QLabel("Delay gas - MW")
        delay_gas_field = QLineEdit()
        timing_form.addRow(delay_gas_label, delay_gas_field)

        self.addWidget(timing_group)

    def show_more_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()
