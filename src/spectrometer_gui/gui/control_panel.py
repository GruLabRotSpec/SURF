from __future__ import annotations
from pathlib import Path
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
    QCheckBox,
    QLineEdit,
)
from zaber_motion import Units

from gui.spectrometer_controller import SpectrometerController
from gui.custom_toolbar import CustomToolbar
from gui.signal_enums import ZaberSpeed


class ControlRegistry:
    def __init__(self, spec_controller):
        self._controller = spec_controller
        self._controls: list[tuple[str, object]] = []

    def register(self, path: str, widget):
        self._controls.append((path, widget))

    def _resolve(self, path: str) -> tuple[object, str]:
        keys = path.strip().split(".")
        obj = self._controller.config
        for key in keys[:-1]:
            obj = getattr(obj, key)
        return obj, keys[-1]

    @staticmethod
    def _get_value(widget):
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, (QCheckBox, QRadioButton)):
            return widget.isChecked()
        elif isinstance(widget, QLineEdit):
            return widget.text()
        else:
            raise TypeError(f"Unsupported widget type: {type(widget)}")

    @staticmethod
    def _set_value(widget, value):
        if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            widget.setValue(value)
        elif isinstance(widget, QComboBox):
            widget.setCurrentText(str(value))
        elif isinstance(widget, (QCheckBox, QRadioButton)):
            widget.setChecked(bool(value))
        elif isinstance(widget, QLineEdit):
            widget.setText(str(value))
        else:
            raise TypeError(f"Unsupported widget type: {type(widget)}")

    def load_config(self):
        for path, widget in self._controls:
            obj, key = self._resolve(path)
            self._set_value(widget, getattr(obj, key))

    def apply_config(self):
        for path, widget in self._controls:
            obj, key = self._resolve(path)
            setattr(obj, key, self._get_value(widget))


class ControlPanel(QWidget):
    def __init__(self, spectrometer: SpectrometerController):
        super().__init__()

        self.spec_controller = spectrometer
        self.registry = ControlRegistry(self.spec_controller)

        self.spec_controller.signal.zaber_position.connect(self.on_zaber_position)
        self.spec_controller.signal.settings_updated.connect(self.on_settings_updated)
        self.spec_controller.misc_signals.config_updated.connect(
            self._set_values_in_control_panel
        )

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

        left_column.addWidget(self._create_zaber_group())
        left_column.addWidget(self._create_awg_group())
        left_column.addWidget(self._create_valon_group())

        # Right Column
        right_column = QVBoxLayout()
        right_column_panel = QWidget()
        right_column_panel.setLayout(right_column)

        right_column.addWidget(self._create_timing_group())
        right_column.addWidget(self._create_oscilloscope_group())

        bottom_layout.addWidget(left_column_panel)
        bottom_layout.addWidget(right_column_panel)

        bottom_layout.setStretch(0, 1)
        bottom_layout.setStretch(1, 1)

        layout.addWidget(bottom_panel)
        layout.addStretch()

    def _create_zaber_group(self) -> QGroupBox:
        zaber_group = QGroupBox("Zaber")

        zaber_form = QFormLayout()
        zaber_group.setLayout(zaber_form)

        zaber_speed_2_label = QLabel("Moving speed")
        self.zaber_speed_2_field = QDoubleSpinBox(
            minimum=0, maximum=2, singleStep=0.1, suffix=" mm/s"
        )
        self.zaber_apply_btn = QPushButton("Apply")
        zaber_form.addRow(zaber_speed_2_label, self.zaber_speed_2_field)
        zaber_form.addRow(self.zaber_apply_btn)

        zaber_control_widget_1 = QHBoxLayout()

        self.zaber_home_btn = QPushButton()
        icon_path = str(Path(__file__).parent / "icons/house.svg")
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

        self.zaber_pos_field = QDoubleSpinBox(
            minimum=0, maximum=50, singleStep=1, suffix=" mm", decimals=3
        )
        zaber_control_widget_1.addWidget(self.zaber_pos_field)

        self.zaber_go_btn = QPushButton()
        self.zaber_go_btn.setIcon(
            QIcon(str(Path(__file__).parent / "icons/crosshair.svg"))
        )
        self.zaber_go_btn.setToolTip("Go to position")
        self.zaber_go_btn.setFixedSize(30, 30)
        self.zaber_go_btn.clicked.connect(self.set_zaber_position)
        zaber_control_widget_1.addWidget(self.zaber_go_btn)

        zaber_form.addRow("Position (absolute)", zaber_control_widget_1)

        zaber_control_widget_2 = QHBoxLayout()

        self.zaber_move_left_btn = QPushButton()
        icon_path = str(Path(__file__).parent / "icons/chevrons_left.svg")
        self.zaber_move_left_btn.setIcon(QIcon(icon_path))
        self.zaber_move_left_btn.setToolTip("Move left by increment")
        self.zaber_move_left_btn.setFixedSize(30, 30)
        self.zaber_move_left_btn.setEnabled(False)
        self.zaber_move_left_btn.clicked.connect(self.set_zaber_position_relative)
        zaber_control_widget_2.addWidget(self.zaber_move_left_btn)

        self.zaber_inc_field = QDoubleSpinBox(
            minimum=-50,
            maximum=50,
            singleStep=1,
            suffix=" mm",
            decimals=3,
        )
        zaber_control_widget_2.addWidget(self.zaber_inc_field)

        self.zaber_move_right_btn = QPushButton()
        self.zaber_move_right_btn.setIcon(
            QIcon(str(Path(__file__).parent / "icons/chevrons_right.svg"))
        )
        self.zaber_move_right_btn.setToolTip("Move right by increment")
        self.zaber_move_right_btn.setFixedSize(30, 30)
        self.zaber_move_right_btn.setEnabled(False)
        self.zaber_move_right_btn.clicked.connect(self.set_zaber_position_relative)
        zaber_control_widget_2.addWidget(self.zaber_move_right_btn)

        zaber_form.addRow("Position (relative)", zaber_control_widget_2)

        self.registry.register(
            "zaber_controller.zaber_moving_speed", self.zaber_speed_2_field
        )

        return zaber_group

    def _create_awg_group(self) -> QGroupBox:
        awg_group = QGroupBox("Arbitrary Waveform Generator (IF)")

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
        self.awg_freq_field = QSpinBox(suffix=" MHz")
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

        awg_apply_widget = QHBoxLayout()
        self.awg_apply_btn = QPushButton("Apply")
        #self.awg_apply_btn.clicked.connect()                  # still need to connect here
        awg_apply_widget.addWidget(self.awg_apply_btn)
        awg_form.addRow( awg_apply_widget)

        self.registry.register(
            "awg_controller.awg_status",
            self.awg_on_btn,
        )
        self.registry.register(
            "awg_controller.awg_run_mode",
            self.run_mode_field,
        )
        self.registry.register(
            "awg_controller.awg_freq",
            self.awg_freq_field,
        )
        self.registry.register(
            "awg_controller.awg_ch_1_output",
            self.awg_ch_1_output_on_btn,
        )
        self.registry.register(
            "awg_controller.awg_ch_2_output",
            self.awg_ch_2_output_on_btn,
        )

        return awg_group

    def _create_valon_group(self) -> QGroupBox:
        valon_group = QGroupBox("Valon (LO)")

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

        self.synth_power_on_btn = QRadioButton("On")
        self.synth_power_off_btn = QRadioButton("Off")
        self.synth_power_on_btn.setChecked(True)

        synth_power_group_widget = QHBoxLayout()
        synth_power_group_widget.addWidget(self.synth_power_on_btn)
        synth_power_group_widget.addWidget(self.synth_power_off_btn)

        synth_power_label = QLabel("Synth power")
        valon_form.addRow(synth_power_label, synth_power_group_widget)

        rf_label = QLabel("RF level (power)")
        self.rf_field = QSpinBox(minimum=-20, maximum=20, suffix=" dBm")
        valon_form.addRow(rf_label, self.rf_field)

        self.synth_power_on_btn = QRadioButton("On")
        self.synth_power_off_btn = QRadioButton("Off")
        self.synth_power_on_btn.setChecked(True)

        ref_source_label = QLabel("Reference source")
        self.ref_source_field = QComboBox()
        self.ref_source_field.addItems(["Internal", "External"])
        valon_form.addRow(ref_source_label, self.ref_source_field)

        ref_freq_label = QLabel("Reference frequency")
        self.ref_freq_field = QDoubleSpinBox(value=10, suffix=" MHz")
        valon_form.addRow(ref_freq_label, self.ref_freq_field)

        freq_label = QLabel("Frequency")
        self.freq_field = QDoubleSpinBox(
            value=8000, suffix=" MHz", minimum=7970, maximum=18000
        )
        valon_form.addRow(freq_label, self.freq_field)

        valon_apply_layout = QHBoxLayout()
        self.valon_apply_btn = QPushButton("Apply")
        # self.valon_apply_btn.clicked.connect()                  # still need to connect here
        valon_apply_layout.addWidget(self.valon_apply_btn)
        valon_form.addRow(valon_apply_layout)

        self.registry.register(
            "valon_controller.rf_output",
            self.rf_output_on_btn,
        )
        self.registry.register(
            "valon_controller.rf_level",
            self.rf_field,
        )
        self.registry.register(
            "valon_controller.synth_power",
            self.synth_power_on_btn,
        )
        self.registry.register(
            "valon_controller.ref_source",
            self.ref_source_field,
        )
        self.registry.register(
            "valon_controller.ref_freq",
            self.ref_freq_field,
        )
        self.registry.register(
            "valon_controller.freq",
            self.freq_field,
        )

        return valon_group

    def _create_timing_group(self) -> QGroupBox:
        timing_group = QGroupBox("Delay Generator")

        timing_form = QFormLayout()
        timing_group.setLayout(timing_form)

        trigger_rate_label = QLabel("Trigger Rate")
        self.trigger_rate_field = QDoubleSpinBox(minimum=0, suffix=" Hz")
        timing_form.addRow(trigger_rate_label, self.trigger_rate_field)

        self.trigger_state_int_btn = QRadioButton("INT")
        self.trigger_state_ext_btn = QRadioButton("EXT")
        self.trigger_state_ext_btn.setChecked(True)

        self.trigger_state_group = QButtonGroup()
        self.trigger_state_group.addButton(self.trigger_state_int_btn)
        self.trigger_state_group.addButton(self.trigger_state_ext_btn)

        trigger_state_group_widget = QHBoxLayout()
        trigger_state_group_widget.addWidget(self.trigger_state_int_btn)
        trigger_state_group_widget.addWidget(self.trigger_state_ext_btn)

        trigger_state_label = QLabel("Trigger State")
        timing_form.addRow(trigger_state_label, trigger_state_group_widget)

        self.registry.register(
            "delay_generator_controller.trigger_rate",
            self.trigger_rate_field,
        )
        self.registry.register(
            "delay_generator_controller.trigger_state", self.trigger_state_int_btn
        )

        self.gas_pulse_on_btn = QRadioButton("On")
        self.gas_pulse_off_btn = QRadioButton("Off")
        self.gas_pulse_on_btn.setChecked(False)

        self.gas_pulse_group = QButtonGroup()
        self.gas_pulse_group.addButton(self.gas_pulse_on_btn)
        self.gas_pulse_group.addButton(self.gas_pulse_off_btn)

        gas_pulse_group_widget = QHBoxLayout()
        gas_pulse_group_widget.addWidget(self.synth_power_on_btn)
        gas_pulse_group_widget.addWidget(self.synth_power_off_btn)

        gas_pulse_label = QLabel("Gas Pulse ")

        timing_form.addRow(gas_pulse_label, gas_pulse_group_widget)

        timing_apply_layout = QHBoxLayout()
        self.timing_apply_btn = QPushButton("Apply")
        # self.timing_apply_btn.clicked.connect()                  # still need to connect here
        timing_apply_layout.addWidget(self.timing_apply_btn)
        timing_form.addRow(timing_apply_layout)

        return timing_group

    def _create_oscilloscope_group(self) -> QGroupBox:
        general_group = QGroupBox("General")
        general_form = QFormLayout()
        general_group.setLayout(general_form)

        preset_layout = QHBoxLayout()
        preset_layout.setContentsMargins(0, 0, 0, 0)
        self.preset_combo = QComboBox()
        self._populate_preset_dropdown()
        self.recall_btn = QPushButton("Recall")
        self.recall_btn.clicked.connect(self._recall_preset)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addWidget(self.recall_btn)
        preset_label = QLabel("Preset")
        general_form.addRow(preset_label, preset_layout)

        sample_rate_label = QLabel("Sample rate")
        self.sample_rate_field = QSpinBox(
            minimum=0, maximum=1000, singleStep=100, suffix=" MS/s"
        )
        general_form.addRow(sample_rate_label, self.sample_rate_field)

        cavity_type_label = QLabel("Cavity Type")
        self.cavity_type_field = QComboBox()
        self.cavity_type_field.addItems(["Continuous", "Pulsed"])
        general_form.addRow(cavity_type_label, self.cavity_type_field)


        math3_group = QGroupBox("Math 3")
        math3_form = QFormLayout()
        math3_group.setLayout(math3_form)

        math3_window_label = QLabel("Apodization")
        self.math3_window_field = QComboBox()
        self.math3_window_field.addItems(
            ["Rectangular", "Hamming", "Hanning", "Blackman"]
        )
        self.math3_window_field.setCurrentText("Rectangular")
        math3_form.addRow(math3_window_label, self.math3_window_field)

        math3_res_label = QLabel("Resolution")
        self.math3_res_field = QDoubleSpinBox(
            minimum=0, maximum=100000, suffix=" kHz", value=890.0
        )
        math3_form.addRow(math3_res_label, self.math3_res_field)

        math3_gatepos_label = QLabel("Gate position")
        self.math3_gatepos_field = QDoubleSpinBox(suffix=" us", value=0.6)
        math3_form.addRow(math3_gatepos_label, self.math3_gatepos_field)

        math3_math_averages_label = QLabel("Math averages")
        self.math3_math_averages_field = QSpinBox(minimum=2, maximum=1000000)
        math3_form.addRow(math3_math_averages_label, self.math3_math_averages_field)

        math3_apply_layout = QHBoxLayout()
        self.math3_apply_btn = QPushButton("Apply")
        # self.math3_apply_btn.clicked.connect()                  # still need to connect here
        math3_apply_layout.addWidget(self.math3_apply_btn)
        math3_form.addRow(math3_apply_layout)

        self.registry.register(
            "oscilloscope_controller.math3.window",
            self.math3_window_field,
        )
        self.registry.register(
            "oscilloscope_controller.math3.resolution",
            self.math3_res_field,
        )
        self.registry.register(
            "oscilloscope_controller.math3.gate_position",
            self.math3_gatepos_field,
        )

        math4_group = QGroupBox("Math 4")
        math4_form = QFormLayout()
        math4_group.setLayout(math4_form)

        math4_window_label = QLabel("Apodization")
        self.math4_window_field = QComboBox()
        self.math4_window_field.addItems(
            ["Rectangular", "Hamming", "Hanning", "Blackman"]
        )
        self.math4_window_field.setCurrentText("Hanning")
        math4_form.addRow(math4_window_label, self.math4_window_field)

        math4_res_label = QLabel("Resolution")
        self.math4_res_field = QDoubleSpinBox(
            minimum=0, maximum=100000, suffix=" kHz", value=100.0
        )
        math4_form.addRow(math4_res_label, self.math4_res_field)

        math4_gatepos_label = QLabel("Gate position")
        self.math4_gatepos_field = QDoubleSpinBox(suffix=" us", value=18.45)
        math4_form.addRow(math4_gatepos_label, self.math4_gatepos_field)

        math4_math_averages_label = QLabel("Math averages")
        self.math4_math_averages_field = QSpinBox(minimum=2, maximum=1000000, value=1000000)
        math4_form.addRow(math4_math_averages_label, self.math4_math_averages_field)

        math4_apply_layout = QHBoxLayout()
        self.math4_apply_btn = QPushButton("Apply")
        # self.math4_apply_btn.clicked.connect()                  # still need to connect here
        math4_apply_layout.addWidget(self.math4_apply_btn)
        math4_form.addRow(math4_apply_layout)

        self.registry.register(
            "oscilloscope_controller.math4.window",
            self.math4_window_field,
        )
        self.registry.register(
            "oscilloscope_controller.math4.resolution",
            self.math4_res_field,
        )
        self.registry.register(
            "oscilloscope_controller.math4.gate_position",
            self.math4_gatepos_field,
        )

        oscilloscope_group = QGroupBox("Oscilloscope")
        oscilloscope_layout = QVBoxLayout()
        oscilloscope_group.setLayout(oscilloscope_layout)

        oscilloscope_layout.addWidget(general_group)
        oscilloscope_layout.addWidget(math3_group)
        oscilloscope_layout.addWidget(math4_group)

        self.registry.register(
            "oscilloscope_controller.sample_rate",
            self.sample_rate_field,
        )
        # self.registry.register(               # Todo: replace with new averages 
        #     "oscilloscope_controller.math_averages",
        #     self.math_averages_field,
        # )

        return oscilloscope_group

    @Slot(float)
    def on_zaber_position(self, position):
        if position != -1:
            self.zaber_slider.setValue(int(position))
            if not self.zaber_pos_field.hasFocus():
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
        if self.spec_controller.current_task:
            print("Cannot move Zaber during a task")
        else:
            print("Attempting to manually move Zaber...")
            new_pos = float(self.zaber_pos_field.value())
            if home:
                self.spec_controller.spectrometer.zaber_controller.home(False)
            else:
                self.spec_controller.spectrometer.zaber_controller.move_to(
                    new_pos, ZaberSpeed.MOVING, False
                )

    def set_zaber_position_relative(self):
        self.spec_controller.spectrometer.zaber_controller.axis.move_relative(
            self.zaber_inc_field.value(), unit=Units.LENGTH_MILLIMETRES
        )  # Temp fix

    def _recall_preset(self):
        preset = self.preset_combo.currentData()
        if preset:
            self.spec_controller.spectrometer.oscilloscope_controller.recall_setup(
                preset.path, self.spec_controller.settings.scope_preset.root_path
            )

    @Slot(object)
    def on_settings_updated(self, settings):
        self.spec_controller.settings = settings
        self._populate_preset_dropdown()

    def _populate_preset_dropdown(self):
        self.preset_combo.clear()
        if self.spec_controller.settings.scope_preset.presets:
            for _, preset in self.spec_controller.settings.scope_preset.presets.items():
                self.preset_combo.addItem(preset.name, preset)
        else:
            self.preset_combo.addItem("None")

    def showEvent(self, event: QShowEvent):
        super().showEvent(event)
        self.registry.load_config()

    @Slot()
    def _set_values_in_control_panel(self):
        self.registry.load_config()

    def _apply_values_in_control_panel(self):
        if not self.spec_controller.current_task:
            self.registry.apply_config()
            self.spec_controller.set_config(self.spec_controller.config)
        else:
            print("Cannot update control options during a task")
