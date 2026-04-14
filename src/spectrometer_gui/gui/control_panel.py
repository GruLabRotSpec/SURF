from __future__ import annotations
import os
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon, QShowEvent
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QComboBox,
    QSlider,
    QSpinBox,
    QDoubleSpinBox,
    QRadioButton,
    QButtonGroup,
)

from gui.spectrometer_controller import SpectrometerController
from gui.settings_window import SettingsWindow
from gui.custom_toolbar import CustomToolbar
#from spectrometer_gui.zaber_controller import ZaberSpeed


class ControlPanel(QWidget):
    def __init__(self, spectrometer: SpectrometerController):
        super().__init__()

        self.spectrometer = spectrometer

        self.spectrometer.signal.zaber_position.connect(self.on_zaber_position)

        layout = QVBoxLayout()
        self.setLayout(layout)

        toolbar = CustomToolbar()
        toolbar.update_action.triggered.connect(self._apply_values_in_control_panel)
        layout.addWidget(toolbar)

        # Bottom columns
        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        bottom_panel = QWidget()
        bottom_panel.setLayout(bottom_layout)

        # Left Column
        left_column = QVBoxLayout()
        left_column_panel = QWidget()
        left_column_panel.setLayout(left_column)

        # left_column.addStretch(1)

        zaber_group = QGroupBox("Zaber")

        zaber_form = QFormLayout()
        zaber_group.setLayout(zaber_form)

        zaber_speed_1_label = QLabel("Scanning speed")
        self.zaber_speed_1_field = QDoubleSpinBox(decimals=3)
        self.zaber_speed_1_field.setMinimum(0)
        self.zaber_speed_1_field.setMaximum(1)
        self.zaber_speed_1_field.setSingleStep(0.001)
        self.zaber_speed_1_field.setSuffix(" mm/s")
        zaber_form.addRow(zaber_speed_1_label, self.zaber_speed_1_field)

        zaber_speed_2_label = QLabel("Moving speed")
        self.zaber_speed_2_field = QDoubleSpinBox()
        self.zaber_speed_2_field.setMinimum(0)
        self.zaber_speed_2_field.setMaximum(5)
        self.zaber_speed_2_field.setSingleStep(0.25)
        self.zaber_speed_2_field.setSuffix(" mm/s")
        zaber_form.addRow(zaber_speed_2_label, self.zaber_speed_2_field)

        zaber_step_size_label = QLabel("Step size")
        self.zaber_step_size_field = QDoubleSpinBox()
        self.zaber_step_size_field.setMinimum(0)
        self.zaber_step_size_field.setMaximum(5)
        self.zaber_step_size_field.setSingleStep(0.25)
        self.zaber_step_size_field.setSuffix(" mm")
        self.zaber_step_size_field.setEnabled(False)
        zaber_form.addRow(zaber_step_size_label, self.zaber_step_size_field)

        zaber_control_widget_1 = QHBoxLayout()

        self.zaber_home_btn = QPushButton()
        icon_path = os.path.join(os.path.dirname(__file__), "icons/house.svg")
        self.zaber_home_btn.setIcon(QIcon(icon_path))
        self.zaber_home_btn.setToolTip("Home")
        self.zaber_home_btn.setFixedSize(30, 30)
        self.zaber_home_btn.setEnabled(False)
        self.zaber_home_btn.clicked.connect(lambda: self.set_zaber_position(True))
        zaber_control_widget_1.addWidget(self.zaber_home_btn)

        self.zaber_slider = QSlider(Qt.Orientation.Horizontal)
        self.zaber_slider.setMinimum(0)
        self.zaber_slider.setMaximum(50)
        self.zaber_slider.setSingleStep(1)
        self.zaber_slider.setEnabled(False)
        zaber_control_widget_1.addWidget(self.zaber_slider)

        self.zaber_pos_field = QDoubleSpinBox()
        self.zaber_pos_field.setMinimum(0)
        self.zaber_pos_field.setMaximum(50)
        self.zaber_pos_field.setSingleStep(1)
        self.zaber_pos_field.setSuffix(" mm")
        zaber_control_widget_1.addWidget(self.zaber_pos_field)

        self.zaber_go_btn = QPushButton()
        self.zaber_go_btn.setIcon(
            QIcon(os.path.join(os.path.dirname(__file__), "icons/crosshair.svg"))
        )
        self.zaber_go_btn.setToolTip("Go to position")
        self.zaber_go_btn.setFixedSize(30, 30)
        self.zaber_go_btn.clicked.connect(self.set_zaber_position)
        zaber_control_widget_1.addWidget(self.zaber_go_btn)

        zaber_form.addRow("Position (absolute)", zaber_control_widget_1)

        zaber_control_widget_2 = QHBoxLayout()

        self.zaber_move_left_btn = QPushButton()
        icon_path = os.path.join(os.path.dirname(__file__), "icons/chevrons_left.svg")
        self.zaber_move_left_btn.setIcon(QIcon(icon_path))
        self.zaber_move_left_btn.setToolTip("Move left by increment")
        self.zaber_move_left_btn.setFixedSize(30, 30)
        self.zaber_move_left_btn.setEnabled(False)
        self.zaber_move_left_btn.clicked.connect(self.set_zaber_position_relative)
        zaber_control_widget_2.addWidget(self.zaber_move_left_btn)

        self.zaber_inc_field = QDoubleSpinBox()
        self.zaber_inc_field.setMinimum(-50)
        self.zaber_inc_field.setMaximum(50)
        self.zaber_inc_field.setSingleStep(1)
        self.zaber_inc_field.setSuffix(" mm")
        zaber_control_widget_2.addWidget(self.zaber_inc_field)

        self.zaber_move_right_btn = QPushButton()
        self.zaber_move_right_btn.setIcon(
            QIcon(os.path.join(os.path.dirname(__file__), "icons/chevrons_right.svg"))
        )
        self.zaber_move_right_btn.setToolTip("Move right by increment")
        self.zaber_move_right_btn.setFixedSize(30, 30)
        self.zaber_move_right_btn.setEnabled(False)
        self.zaber_move_right_btn.clicked.connect(self.set_zaber_position_relative)
        zaber_control_widget_2.addWidget(self.zaber_move_right_btn)

        zaber_form.addRow("Position (relative)", zaber_control_widget_2)

        left_column.addWidget(zaber_group)

        awg_group = QGroupBox("Arbitrary Waveform Generator")

        awg_form = QFormLayout()
        awg_group.setLayout(awg_form)

        self.awg_on_btn = QRadioButton("Run")
        self.awg_off_btn = QRadioButton("Stop")
        self.awg_off_btn.setChecked(True)

        self.awg_run_group = QButtonGroup()
        self.awg_run_group.addButton(self.awg_on_btn)
        self.awg_run_group.addButton(self.awg_off_btn)

        awg_run_group_widget = QHBoxLayout()
        awg_run_group_widget.addWidget(self.awg_on_btn)
        awg_run_group_widget.addWidget(self.awg_off_btn)

        status_label = QLabel("Status")
        awg_form.addRow(status_label, awg_run_group_widget)

        run_mode_label = QLabel("Run mode")
        self.run_mode_field = QComboBox()
        self.run_mode_field.addItems(["Continuous", "Triggered"])
        awg_form.addRow(run_mode_label, self.run_mode_field)

        awg_freq_label = QLabel("Frequency")
        self.awg_freq_field = QSpinBox()
        self.awg_freq_field.setSuffix(" MHz")
        awg_form.addRow(awg_freq_label, self.awg_freq_field)

        self.awg_ch_1_output_on_btn = QRadioButton("On")
        self.awg_ch_1_output_off_btn = QRadioButton("Off")
        self.awg_ch_1_output_off_btn.setChecked(True)

        self.awg_ch_1_output_group = QButtonGroup()
        self.awg_ch_1_output_group.addButton(self.awg_ch_1_output_on_btn)
        self.awg_ch_1_output_group.addButton(self.awg_ch_1_output_off_btn)

        awg_ch_1_output_group_widget = QHBoxLayout()
        awg_ch_1_output_group_widget.addWidget(self.awg_ch_1_output_on_btn)
        awg_ch_1_output_group_widget.addWidget(self.awg_ch_1_output_off_btn)

        ch_1_label = QLabel("Channel 1 output")
        awg_form.addRow(ch_1_label, awg_ch_1_output_group_widget)

        self.awg_ch_2_output_on_btn = QRadioButton("On")
        self.awg_ch_2_output_off_btn = QRadioButton("Off")
        self.awg_ch_2_output_off_btn.setChecked(True)

        self.awg_ch_2_output_group = QButtonGroup()
        self.awg_ch_2_output_group.addButton(self.awg_ch_2_output_on_btn)
        self.awg_ch_2_output_group.addButton(self.awg_ch_2_output_off_btn)

        awg_ch_2_output_group_widget = QHBoxLayout()
        awg_ch_2_output_group_widget.addWidget(self.awg_ch_2_output_on_btn)
        awg_ch_2_output_group_widget.addWidget(self.awg_ch_2_output_off_btn)

        ch_2_label = QLabel("Channel 2 output")
        awg_form.addRow(ch_2_label, awg_ch_2_output_group_widget)

        left_column.addWidget(awg_group)

        valon_group = QGroupBox("Valon")

        valon_form = QFormLayout()
        valon_group.setLayout(valon_form)

        self.rf_output_on_btn = QRadioButton("On")
        self.rf_output_off_btn = QRadioButton("Off")
        self.rf_output_on_btn.setChecked(True)

        self.rf_output_group = QButtonGroup()
        self.rf_output_group.addButton(self.rf_output_on_btn)
        self.rf_output_group.addButton(self.rf_output_off_btn)

        rf_output_group_widget = QHBoxLayout()
        rf_output_group_widget.addWidget(self.rf_output_on_btn)
        rf_output_group_widget.addWidget(self.rf_output_off_btn)

        rf_output_label = QLabel("RF output")
        valon_form.addRow(rf_output_label, rf_output_group_widget)

        rf_label = QLabel("RF level (power)")
        self.rf_field = QSpinBox()
        self.rf_field.setMinimum(0)
        self.rf_field.setMaximum(20)
        self.rf_field.setSuffix(" dBm")
        valon_form.addRow(rf_label, self.rf_field)

        self.synth_power_on_btn = QRadioButton("On")
        self.synth_power_off_btn = QRadioButton("Off")
        self.synth_power_on_btn.setChecked(True)

        self.synth_power_group = QButtonGroup()
        self.synth_power_group.addButton(self.synth_power_on_btn)
        self.synth_power_group.addButton(self.synth_power_off_btn)

        synth_power_group_widget = QHBoxLayout()
        synth_power_group_widget.addWidget(self.synth_power_on_btn)
        synth_power_group_widget.addWidget(self.synth_power_off_btn)

        synth_power_label = QLabel("Synth power")
        valon_form.addRow(synth_power_label, synth_power_group_widget)

        ref_source_label = QLabel("Reference source")
        self.ref_source_field = QComboBox()
        self.ref_source_field.addItems(["Internal", "External"])
        valon_form.addRow(ref_source_label, self.ref_source_field)

        ref_freq_label = QLabel("Reference frequency")
        self.ref_freq_field = QDoubleSpinBox()
        self.ref_freq_field.setValue(10)
        self.ref_freq_field.setSuffix(" MHz")
        valon_form.addRow(ref_freq_label, self.ref_freq_field)

        left_column.addWidget(valon_group)

        # Right Column
        right_column = QVBoxLayout()
        right_column_panel = QWidget()
        right_column_panel.setLayout(right_column)

        # right_column.addStretch(1)

        timing_group = QGroupBox("Delay Generator")

        timing_form = QFormLayout()
        timing_group.setLayout(timing_form)

        trigger_rate_label = QLabel("Trigger Rate")
        self.trigger_rate_field = QDoubleSpinBox()
        self.trigger_rate_field.setMinimum(0)
        self.trigger_rate_field.setSuffix(" Hz")
        timing_form.addRow(trigger_rate_label, self.trigger_rate_field)

        right_column.addWidget(timing_group)

        # Oscilloscope group boxes
        general_group = QGroupBox("General")
        general_form = QFormLayout()
        general_group.setLayout(general_form)

        acq_rate_label = QLabel("Acquisition rate")
        self.acq_rate_field = QSpinBox()
        self.acq_rate_field.setMinimum(1)
        self.acq_rate_field.setMaximum(10000)
        general_form.addRow(acq_rate_label, self.acq_rate_field)

        sample_rate_label = QLabel("Sample rate")
        self.sample_rate_field = QSpinBox()
        self.sample_rate_field.setMinimum(0)
        self.sample_rate_field.setSingleStep(100)
        self.sample_rate_field.setMaximum(1000)
        self.sample_rate_field.setSuffix(" MS/s")
        general_form.addRow(sample_rate_label, self.sample_rate_field)

        math_averages_label = QLabel("Math averages")
        self.math_averages_field = QSpinBox()
        self.math_averages_field.setMinimum(2)
        self.math_averages_field.setMaximum(1000000)
        general_form.addRow(math_averages_label, self.math_averages_field)

        math3_group = QGroupBox("Math 3")
        math3_form = QFormLayout()
        math3_group.setLayout(math3_form)

        math3_window_label = QLabel("Window")
        self.math3_window_field = QComboBox()
        self.math3_window_field.addItems(
            ["Rectangular", "Hamming", "Hanning", "Blackman"]
        )
        self.math3_window_field.setCurrentText("Rectangular")
        math3_form.addRow(math3_window_label, self.math3_window_field)

        math3_res_label = QLabel("Resolution")
        self.math3_res_field = QDoubleSpinBox()
        self.math3_res_field.setMinimum(0)
        self.math3_res_field.setMaximum(100000)
        self.math3_res_field.setSuffix(" kHz")
        self.math3_res_field.setValue(890.0)
        math3_form.addRow(math3_res_label, self.math3_res_field)

        math3_gatepos_label = QLabel("Gate position")
        self.math3_gatepos_field = QDoubleSpinBox()
        self.math3_gatepos_field.setSuffix(" us")
        self.math3_gatepos_field.setValue(0.6)
        math3_form.addRow(math3_gatepos_label, self.math3_gatepos_field)

        math4_group = QGroupBox("Math 4")
        math4_form = QFormLayout()
        math4_group.setLayout(math4_form)

        math4_window_label = QLabel("Window")
        self.math4_window_field = QComboBox()
        self.math4_window_field.addItems(
            ["Rectangular", "Hamming", "Hanning", "Blackman"]
        )
        self.math4_window_field.setCurrentText("Hanning")
        math4_form.addRow(math4_window_label, self.math4_window_field)

        math4_res_label = QLabel("Resolution")
        self.math4_res_field = QDoubleSpinBox()
        self.math4_res_field.setMinimum(0)
        self.math4_res_field.setMaximum(100000)
        self.math4_res_field.setSuffix(" kHz")
        self.math4_res_field.setValue(100.0)
        math4_form.addRow(math4_res_label, self.math4_res_field)

        math4_gatepos_label = QLabel("Gate position")
        self.math4_gatepos_field = QDoubleSpinBox()
        self.math4_gatepos_field.setSuffix(" us")
        self.math4_gatepos_field.setValue(18.45)
        math4_form.addRow(math4_gatepos_label, self.math4_gatepos_field)

        oscilloscope_group = QGroupBox("Oscilloscope")
        oscilloscope_layout = QVBoxLayout()
        oscilloscope_group.setLayout(oscilloscope_layout)
        oscilloscope_layout.addWidget(general_group)
        oscilloscope_layout.addWidget(math3_group)
        oscilloscope_layout.addWidget(math4_group)

        right_column.addWidget(oscilloscope_group)

        bottom_layout.addWidget(left_column_panel)
        bottom_layout.addWidget(right_column_panel)

        bottom_layout.setStretch(0, 1)
        bottom_layout.setStretch(1, 1)

        layout.addWidget(bottom_panel)
        layout.addStretch()

    @Slot(float)
    def on_zaber_position(self, position):
        if position != -1:
            self.zaber_slider.setValue(int(position))
            self.zaber_pos_field.setValue(position)
            self.zaber_slider.setEnabled(True)
            self.zaber_pos_field.setEnabled(True)
            self.zaber_go_btn.setEnabled(True)
            self.zaber_home_btn.setEnabled(True)
            self.zaber_move_left_btn.setEnabled(True)
            self.zaber_move_right_btn.setEnabled(True)
        else:
            self.zaber_slider.setEnabled(False)
            self.zaber_pos_field.setEnabled(False)
            self.zaber_go_btn.setEnabled(False)
            self.zaber_home_btn.setEnabled(False)
            self.zaber_move_left_btn.setEnabled(False)
            self.zaber_move_right_btn.setEnabled(False)

    def set_zaber_position(self, home=False):
        if self.spectrometer.current_task:
            print("Cannot move Zaber during a task")
        else:
            print("Attempting to manually move Zaber...")
            new_pos = float(self.zaber_pos_field.value())
            if home:
                self.spectrometer.spectrometer.zaber_controller.home(False)
            else:
                self.spectrometer.spectrometer.zaber_controller.move_to(
                    new_pos, 1, False
                )

    def set_zaber_position_relative(self):
        self.spectrometer.spectrometer.zaber_controller.axis.move_relative(self.zaber_inc_field.value()) # Temp fix

    def show_more_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self._set_values_in_control_panel()

    def _set_values_in_control_panel(self):
        print(self.spectrometer.config)

        # Zaber
        self.zaber_speed_1_field.setValue(
            self.spectrometer.config.zaber_controller.zaber_scanning_speed
        )
        self.zaber_speed_2_field.setValue(
            self.spectrometer.config.zaber_controller.zaber_moving_speed
        )

        # AWG
        self.awg_on_btn.setChecked(
            True if self.spectrometer.config.awg_controller.awg_status else False
        )
        self.run_mode_field.setCurrentText(
            self.spectrometer.config.awg_controller.awg_run_mode
        )
        self.awg_freq_field.setValue(self.spectrometer.config.awg_controller.awg_freq)
        self.awg_ch_1_output_on_btn.setChecked(
            True if self.spectrometer.config.awg_controller.awg_ch_1_output else False
        )
        self.awg_ch_2_output_on_btn.setChecked(
            True if self.spectrometer.config.awg_controller.awg_ch_2_output else False
        )

        # Valon
        self.rf_output_on_btn.setChecked(
            True if self.spectrometer.config.valon_controller.rf_output else False
        )
        self.rf_field.setValue(self.spectrometer.config.valon_controller.rf_level)
        self.synth_power_on_btn.setChecked(
            True if self.spectrometer.config.valon_controller.synth_power else False
        )
        self.ref_source_field.setCurrentText(
            self.spectrometer.config.valon_controller.ref_source
        )
        self.ref_freq_field.setValue(self.spectrometer.config.valon_controller.ref_freq)

        # Oscilloscope - Math 4
        self.math4_window_field.setCurrentText(
            self.spectrometer.config.oscilloscope_controller.math4.window
        )
        self.math4_res_field.setValue(
            self.spectrometer.config.oscilloscope_controller.math4.resolution
        )
        self.math4_gatepos_field.setValue(
            self.spectrometer.config.oscilloscope_controller.math4.gate_position
        )

        # Oscilloscope - Math 3
        self.math3_window_field.setCurrentText(
            self.spectrometer.config.oscilloscope_controller.math3.window
        )
        self.math3_res_field.setValue(
            self.spectrometer.config.oscilloscope_controller.math3.resolution
        )
        self.math3_gatepos_field.setValue(
            self.spectrometer.config.oscilloscope_controller.math3.gate_position
        )

        # Oscilloscope - General
        self.acq_rate_field.setValue(
            self.spectrometer.config.oscilloscope_controller.acq_rate
        )
        self.sample_rate_field.setValue(
            self.spectrometer.config.oscilloscope_controller.sample_rate
        )
        self.math_averages_field.setValue(
            self.spectrometer.config.oscilloscope_controller.math_averages
        )

        # Delay generator
        self.trigger_rate_field.setValue(
            self.spectrometer.config.delay_generator_controller.trigger_rate
        )

    def _apply_values_in_control_panel(self):
        if not self.spectrometer.current_task:
            # Zaber
            self.spectrometer.config.zaber_controller.zaber_scanning_speed = (
                self.zaber_speed_1_field.value()
            )
            self.spectrometer.config.zaber_controller.zaber_moving_speed = (
                self.zaber_speed_2_field.value()
            )

            # AWG
            self.spectrometer.config.awg_controller.awg_status = (
                True if self.awg_on_btn.isChecked() else False
            )
            self.spectrometer.config.awg_controller.awg_run_mode = (
                self.run_mode_field.currentText()
            )
            self.spectrometer.config.awg_controller.awg_freq = (
                self.awg_freq_field.value()
            )
            self.spectrometer.config.awg_controller.awg_ch_1_output = (
                True if self.awg_ch_1_output_on_btn.isChecked() else False
            )
            self.spectrometer.config.awg_controller.awg_ch_2_output = (
                True if self.awg_ch_2_output_on_btn.isChecked() else False
            )

            # Valon
            self.spectrometer.config.valon_controller.rf_output = (
                True if self.rf_output_on_btn.isChecked() else False
            )
            self.spectrometer.config.valon_controller.rf_level = self.rf_field.value()
            self.spectrometer.config.valon_controller.synth_power = (
                True if self.synth_power_on_btn.isChecked() else False
            )
            self.spectrometer.config.valon_controller.ref_source = (
                self.ref_source_field.currentText()
            )
            self.spectrometer.config.valon_controller.ref_freq = (
                self.ref_freq_field.value()
            )

            # Oscilloscope - Math 4
            self.spectrometer.config.oscilloscope_controller.math4.window = (  # type: ignore[assignment]
                self.math4_window_field.currentText()
            )
            self.spectrometer.config.oscilloscope_controller.math4.resolution = (
                self.math4_res_field.value()
            )
            self.spectrometer.config.oscilloscope_controller.math4.gate_position = (
                self.math4_gatepos_field.value()
            )

            # Oscilloscope - Math 3
            self.spectrometer.config.oscilloscope_controller.math3.window = (  # type: ignore[assignment]
                self.math3_window_field.currentText()
            )
            self.spectrometer.config.oscilloscope_controller.math3.resolution = (
                self.math3_res_field.value()
            )
            self.spectrometer.config.oscilloscope_controller.math3.gate_position = (
                self.math3_gatepos_field.value()
            )

            # Oscilloscope - General
            self.spectrometer.config.oscilloscope_controller.acq_rate = (
                self.acq_rate_field.value()
            )
            self.spectrometer.config.oscilloscope_controller.sample_rate = (
                self.sample_rate_field.value()
            )
            self.spectrometer.config.oscilloscope_controller.math_averages = (
                self.math_averages_field.value()
            )

            # Delay generator
            self.spectrometer.config.delay_generator_controller.trigger_rate = (
                self.trigger_rate_field.value()
            )

            self.spectrometer.set_config(self.spectrometer.config)
        else:
            print("Cannot update control options during a task")
