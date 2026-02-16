import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
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
    QSlider,
    QSpinBox,
    QDoubleSpinBox
)

from gui.spectrometer_controller import SpectrometerController
from gui.settings_window import SettingsWindow


class ControlPanel(QWidget):
    def __init__(self, spectrometer: SpectrometerController):
        super().__init__()

        self.spectrometer = spectrometer

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
        zaber_speed_1_field = QDoubleSpinBox()
        zaber_speed_1_field.setMinimum(0)
        zaber_speed_1_field.setMaximum(1)
        zaber_speed_1_field.setSingleStep(.1)
        zaber_speed_1_field.setSuffix("mm/s")
        zaber_form.addRow(zaber_speed_1_label, zaber_speed_1_field)

        zaber_speed_2_label = QLabel("Zaber homing speed")
        zaber_speed_2_field = QDoubleSpinBox()
        zaber_speed_2_field.setMinimum(0)
        zaber_speed_2_field.setMaximum(5)
        zaber_speed_2_field.setSingleStep(.25)
        zaber_speed_2_field.setSuffix("mm/s")
        zaber_form.addRow(zaber_speed_2_label, zaber_speed_2_field)

        zaber_control_widget = QHBoxLayout()

        zaber_home_btn = QPushButton()
        icon_path = os.path.join(
            os.path.dirname(__file__), "icons/house.svg"
        )
        zaber_home_btn.setIcon(QIcon(icon_path))
        zaber_home_btn.setToolTip("Home")
        zaber_home_btn.setFixedSize(30, 30)
        zaber_control_widget.addWidget(zaber_home_btn)

        self.zaber_slider = QSlider(Qt.Orientation.Horizontal)
        self.zaber_slider.setMinimum(0)
        self.zaber_slider.setMaximum(50)
        self.zaber_slider.setSingleStep(1)
        self.zaber_slider.setEnabled(False)
        zaber_control_widget.addWidget(self.zaber_slider)

        self.zaber_pos_field = QDoubleSpinBox()
        self.zaber_pos_field.setMinimum(0)
        self.zaber_pos_field.setMaximum(50)
        self.zaber_pos_field.setSingleStep(1)
        self.zaber_pos_field.setSuffix("mm")
        zaber_control_widget.addWidget(self.zaber_pos_field)

        zaber_go_btn = QPushButton()
        zaber_go_btn.setIcon(QIcon(os.path.join(
            os.path.dirname(__file__), "icons/crosshair.svg"
        )))
        zaber_go_btn.setToolTip("Go to position")
        zaber_go_btn.setFixedSize(30, 30)
        zaber_go_btn.clicked.connect(self.set_zaber_position)
        zaber_control_widget.addWidget(zaber_go_btn)

        zaber_form.addRow("Manual control", zaber_control_widget)

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
        rf_field = QDoubleSpinBox()
        rf_field.setMinimum(0)
        rf_field.setMaximum(20)
        rf_field.setSuffix("dBm")
        valon_form.addRow(rf_label, rf_field)

        left_column.addWidget(valon_group)

        # Right Column
        right_column = QVBoxLayout()
        right_column_panel = QWidget()
        right_column_panel.setLayout(right_column)

        right_column.addStretch(1)

        oscilloscope_group = QGroupBox("Oscilloscope")

        oscilloscope_form = QFormLayout()
        oscilloscope_group.setLayout(oscilloscope_form)

        resolution_label = QLabel("Resolution")
        resolution_field = QSpinBox()
        resolution_field.setMinimum(0)
        resolution_field.setMaximum(1000000)
        resolution_field.setSuffix("kHz")
        oscilloscope_form.addRow(resolution_label, resolution_field)

        sample_rate_label = QLabel("Sample rate")
        sample_rate_field = QSpinBox()
        sample_rate_field.setMinimum(0)
        sample_rate_field.setSingleStep(100)
        sample_rate_field.setMaximum(1000000)
        sample_rate_field.setSuffix("MS/s")
        oscilloscope_form.addRow(sample_rate_label, sample_rate_field)

        window_type_label = QLabel("Window type")
        window_type_field = QComboBox()
        window_type_field.addItems(["Rectangular", "Hamming", "Hanning", "Blackman"])
        oscilloscope_form.addRow(window_type_label, window_type_field)

        gate_position_label = QLabel("Gate position")
        gate_position_field = QSpinBox()
        gate_position_field.setMinimum(0)
        gate_position_field.setMaximum(1000)
        gate_position_field.setSuffix("μs")
        oscilloscope_form.addRow(gate_position_label, gate_position_field)

        math_avg_label = QLabel("Math averages")
        math_avg_field = QSpinBox()
        math_avg_field.setMinimum(0)
        math_avg_field.setMaximum(1000)
        oscilloscope_form.addRow(math_avg_label, math_avg_field)

        right_column.addWidget(oscilloscope_group)


        timing_group = QGroupBox("Delay generator")

        timing_form = QFormLayout()
        timing_group.setLayout(timing_form)

        delay_gas_label = QLabel("Delay gas - MW")
        delay_gas_field = QDoubleSpinBox()
        delay_gas_field.setMinimum(0)
        delay_gas_field.setSuffix("μs")
        timing_form.addRow(delay_gas_label, delay_gas_field)

        right_column.addWidget(timing_group)

        layout.addWidget(left_column_panel)
        layout.addWidget(right_column_panel)

        layout.setStretch(0, 1)
        layout.setStretch(1, 1)

        self.get_zaber_position()

    def get_zaber_position(self):
        print("Attempting to get Zaber position...")
        try:
            pos = self.spectrometer.spectrometer.zaber_controller.get_pos()
            self.zaber_slider.setValue(pos)
            self.zaber_pos_field.setValue(pos)
        except:
            print("Unable to get Zaber position")


    def set_zaber_position(self):
        if self.spectrometer.current_task:
            print("Cannot move Zaber during a task")
        else:
            print("Attempting to manually move Zaber...")
            new_pos = float(self.zaber_pos_field.value())
            self.spectrometer.spectrometer.zaber_controller.move_to(new_pos)


    def show_more_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()
