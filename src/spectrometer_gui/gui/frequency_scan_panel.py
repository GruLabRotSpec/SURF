from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QGroupBox,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QDoubleSpinBox,
)
import pyqtgraph as pg

from frequency_scan_settings import (
    Experiment,
    ScanParameters,
    DigitizerSettings,
    TimingSettings,
    FrequencyScanSettings,
    OutputSettings,
)
from gui.spectrometer_controller import SpectrometerController
from spectrometer import ScanType, GraphState, CavityTrackState

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class FrequencyScanPanel(QWidget):
    def __init__(self, spectrometer: SpectrometerController):
        super().__init__()

        self.spectrum_x = []
        self.spectrum_y = []
        self.cavity_track_x = []
        self.cavity_track_y = []

        self.spec_controller = spectrometer

        self.spec_controller.signal.scanning.connect(self.on_scanning)
        self.spec_controller.signal.update_graph.connect(self.on_update_graph)
        self.spec_controller.signal.update_cavityTrack.connect(self.on_update_cavityTrack)
        self.spec_controller.signal.zaber_position.connect(self.on_zaber_position)
        self.spec_controller.signal.settings_updated.connect(self.on_settings_updated)

        layout = QVBoxLayout()
        self.setLayout(layout)

        top_row_hbox = QHBoxLayout()
        top_row_hbox.addWidget(self._create_experiment_params_panel(), stretch=1)
        top_row_hbox.addWidget(self._create_scan_settings_panel(), stretch=1)
        top_row_hbox.addWidget(self._create_digitizer_panel(), stretch=1)
        top_row_hbox.addWidget(self._create_timing_panel(), stretch=1)

        layout.addLayout(top_row_hbox, stretch=1)
        layout.addWidget(self._create_spectrum_graph(), stretch=1)

        bottom_hbox = QHBoxLayout()
        bottom_hbox.addWidget(self._create_cavity_track_graph(), stretch=2)
        bottom_hbox.addWidget(self._create_scan_status_group(), stretch=1)

        layout.addLayout(bottom_hbox, stretch=1)

        self.output_folder_field.setText(self.spec_controller.settings.output.filename)
        self.directory_field.setText(self.spec_controller.settings.output.location)

        self.on_update_graph(GraphState(ScanType.FREQUENCY,[], [], []))

    def _create_scan_settings_panel(self) -> QWidget:
        self.scan_settings_group = QGroupBox("Scan")

        scan_form = QFormLayout()
        self.scan_settings_group.setLayout(scan_form)

        start_freq_label = QLabel("Starting Frequency")
        self.start_freq_field = QDoubleSpinBox(
            minimum=8000, maximum=18000, decimals=3, suffix=" MHz", value=10000
        )
        scan_form.addRow(start_freq_label, self.start_freq_field)

        end_freq_label = QLabel("Ending Frequency")
        self.end_freq_field = QDoubleSpinBox(
            minimum=8000, maximum=18000, decimals=3, suffix=" MHz", value=10500
        )
        scan_form.addRow(end_freq_label, self.end_freq_field)

        step_size_label = QLabel("Freq Step Size")
        self.step_size_field = QDoubleSpinBox(
            minimum=0, maximum=1, value=0.5, singleStep=0.25, decimals=3, suffix=" MHz"
        )
        scan_form.addRow(step_size_label, self.step_size_field)

        scanning_speed_label = QLabel("Zaber Speed")
        self.scanning_speed_field = QDoubleSpinBox(
            decimals=3,
            minimum=0,
            maximum=2,
            singleStep=0.001,
            suffix=" mm/s",
            value=0.003,
        )
        scan_form.addRow(scanning_speed_label, self.scanning_speed_field)

        zaber_pos_label = QLabel("Zaber Position")
        zaber_pos_layout = QHBoxLayout()
        self.zaber_pos_field = QDoubleSpinBox(
            minimum=0, maximum=50, decimals=3, suffix=" mm"
        )
        self.zaber_pos_field.setEnabled(False)
        zaber_pos_layout.addWidget(self.zaber_pos_field)
        self.zaber_set_pos_checkbox = QCheckBox("Set Position")
        self.zaber_set_pos_checkbox.setChecked(False)
        self.zaber_set_pos_checkbox.toggled.connect(self.on_zaber_set_pos_toggled)
        zaber_pos_layout.addWidget(self.zaber_set_pos_checkbox)
        scan_form.addRow(zaber_pos_label, zaber_pos_layout)

        cavity_type_label = QLabel("Cavity Type")
        self.cavity_type_field = QComboBox()
        self.cavity_type_field.addItems(["Continuous", "Pulsed"])
        scan_form.addRow(cavity_type_label, self.cavity_type_field)

        acquisition_label = QLabel('# of Acquisitions')
        self.acq_field = QSpinBox(minimum=1,maximum=100000)
        scan_form.addRow(acquisition_label,self.acq_field)



        return self.scan_settings_group

    def _create_experiment_params_panel(self) -> QWidget:
        self.experiment_group = QGroupBox("Experiment")

        experiment_form = QFormLayout()
        self.experiment_group.setLayout(experiment_form)

        sample_name_label = QLabel("Sample name")
        self.sample_name_field = QLineEdit()
        experiment_form.addRow(sample_name_label, self.sample_name_field)

        sample_temp_label = QLabel("Sample temp")
        self.sample_temp_field = QDoubleSpinBox(suffix=" C", maximum=300)
        experiment_form.addRow(sample_temp_label, self.sample_temp_field)

        gas_name_label = QLabel("Gas")
        self.gas_name_field = QLineEdit()
        experiment_form.addRow(gas_name_label, self.gas_name_field)

        gas_width_label = QLabel("Gas width")
        self.gas_width_field = QDoubleSpinBox(
            suffix=" μs",
            value=600,
            maximum=2000,
        )
        experiment_form.addRow(gas_width_label, self.gas_width_field)

        backing_pressure_label = QLabel("Backing pressure")
        self.backing_pressure_field = QDoubleSpinBox(
            value=15, maximum=100, minimum=0, suffix=" psi"
        )
        experiment_form.addRow(backing_pressure_label, self.backing_pressure_field)

        chamber_pressure_label = QLabel("Chamber pressure")
        self.chamber_pressure_field = QLineEdit(text="1.0e-6 torr")
        experiment_form.addRow(chamber_pressure_label, self.chamber_pressure_field)

        mw_width_label = QLabel("MW width")
        self.mw_width_field = QDoubleSpinBox(suffix=" μs")
        experiment_form.addRow(mw_width_label, self.mw_width_field)
        return self.experiment_group

    def _create_digitizer_panel(self) -> QWidget:
        self.digitizer_group = QGroupBox("Digitizer")

        digitizer_form = QFormLayout()
        self.digitizer_group.setLayout(digitizer_form)

        preset_layout = QHBoxLayout()
        preset_layout.setContentsMargins(0, 0, 0, 0)
        self.preset_combo = QComboBox()
        self._populate_preset_dropdown()
        self.recall_btn = QPushButton("Recall")
        self.recall_btn.clicked.connect(self._recall_preset)
        preset_layout.addWidget(self.preset_combo)
        preset_layout.addWidget(self.recall_btn)
        preset_label = QLabel("Oscilloscope Preset")
        digitizer_form.addRow(preset_label, preset_layout)

        resolution_label = QLabel("Resolution")
        self.resolution_field = QSpinBox(
            minimum=1, maximum=16384, value=100, suffix=" kHz"
        )
        digitizer_form.addRow(resolution_label, self.resolution_field)

        acq_window_label = QLabel("Acq Window")
        self.acq_window_field = QDoubleSpinBox(
            minimum=1, maximum=10000, value=100, suffix=" μs"
        )
        digitizer_form.addRow(acq_window_label, self.acq_window_field)



        apodization_label = QLabel("Apodization")
        self.apodization_field = QComboBox()
        self.apodization_field.addItems(["Hanning", "Hamming", "Blackman"])
        digitizer_form.addRow(apodization_label, self.apodization_field)

        return self.digitizer_group

    def _create_timing_panel(self) -> QWidget:
        self.timing_group = QGroupBox("Timing Sequence")

        timing_form = QFormLayout()
        self.timing_group.setLayout(timing_form)

        preset_label = QLabel("Timing Preset")
        timing_preset_layout = QHBoxLayout()
        timing_preset_layout.setContentsMargins(0, 0, 0, 0)
        self.timing_preset_field = QComboBox()
        timing_preset_layout.addWidget(self.timing_preset_field)
        self.timing_recall_btn = QPushButton("Recall")
        timing_preset_layout.addWidget(self.timing_recall_btn)
        timing_form.addRow(preset_label, timing_preset_layout)

        rep_rate_label = QLabel("Rep Rate")
        self.rep_rate_field = QSpinBox(minimum=1, maximum=1000, value=5, suffix=" Hz")
        timing_form.addRow(rep_rate_label, self.rep_rate_field)

        valve_mw_delay_label = QLabel("Valve-mw Delay")
        self.valve_mw_delay_field = QSpinBox(
            minimum=0, maximum=10000, value=1300, suffix=" μs"
        )
        timing_form.addRow(valve_mw_delay_label, self.valve_mw_delay_field)

        spdt_width_label = QLabel("SPDT Width")
        self.spdt_width_field = QDoubleSpinBox(
            minimum=1, maximum=10000, value=10, suffix=" μs"
        )
        timing_form.addRow(spdt_width_label, self.spdt_width_field)

        acq_delay_label = QLabel("Acq Delay")
        self.acq_delay_field = QDoubleSpinBox(
            minimum=0, maximum=10000, value=50, suffix=" μs"
        )
        timing_form.addRow(acq_delay_label, self.acq_delay_field)

        return self.timing_group

    def _create_spectrum_graph(self) -> QWidget:
        self.spectrum_graph = pg.PlotWidget(title="Spectrum")
        self.spectrum_graph.setLabel("bottom", "Frequency (MHz)")
        self.spectrum_graph.setLabel("left", "Relative Intensity (Volts)")
        self.spectrum_graph.showGrid(x=True, y=True, alpha=0.3)
        self.spectrum_graph.plotItem.getViewBox().setMouseEnabled(x=False, y=False)  # type: ignore
        self.spectrum_graph.getPlotItem().layout.setContentsMargins(5, 0, 15, 10)  # type: ignore
        self.spectrum_plot = self.spectrum_graph.plot(pen=pg.mkPen(color="b", width=1))
        return self.spectrum_graph

    def _create_cavity_track_graph(self) -> QWidget:
        self.cavity_track_graph = pg.PlotWidget(title="Cavity Track")
        self.cavity_track_graph.setLabel("bottom", "Frequency (MHz)")
        self.cavity_track_graph.setLabel("left", "Relative Intensity (Volts)")
        self.cavity_track_graph.showGrid(x=True, y=True, alpha=0.3)
        self.cavity_track_graph.plotItem.getViewBox().setMouseEnabled(x=False, y=False)  # type: ignore
        self.cavity_track_graph.getPlotItem().layout.setContentsMargins(5, 0, 15, 10)  # type: ignore
        self.cavity_track_plot = self.cavity_track_graph.plot(
            pen=pg.mkPen(color="b", width=1)
        )
        return self.cavity_track_graph

    def _create_scan_status_group(self) -> QWidget:
        group = QGroupBox("Scan Status")

        scan_status_vbox = QVBoxLayout()
        group.setLayout(scan_status_vbox)

        form_vbox = QVBoxLayout()
        scan_status_vbox.addLayout(form_vbox)

        form = QFormLayout()
        form_vbox.addLayout(form)

        current_freq_label = QLabel("Current Freq")
        self.current_freq_field = QLineEdit()
        self.current_freq_field.setReadOnly(True)
        form.addRow(current_freq_label, self.current_freq_field)

        elapsed_time_label = QLabel("Elapsed Time")
        self.elapsed_time_field = QLineEdit()
        self.elapsed_time_field.setReadOnly(True)
        form.addRow(elapsed_time_label, self.elapsed_time_field)

        time_remaining_label = QLabel("Time Remaining")
        self.time_remaining_field = QLineEdit()
        self.time_remaining_field.setReadOnly(True)
        form.addRow(time_remaining_label, self.time_remaining_field)

        output_folder_label = QLabel("Output Folder")
        self.output_folder_field = QLineEdit()
        form.addRow(output_folder_label, self.output_folder_field)

        directory_label = QLabel("Directory")
        directory_layout = QHBoxLayout()
        directory_layout.setContentsMargins(0, 0, 0, 0)
        self.directory_field = QLineEdit()
        directory_layout.addWidget(self.directory_field)
        self.browse_btn = QPushButton("Browse")
        directory_layout.addWidget(self.browse_btn)
        self.browse_btn.clicked.connect(self.on_browse_directory)
        form.addRow(directory_label, directory_layout)

        buttons_hbox = QHBoxLayout()
        form_vbox.addLayout(buttons_hbox)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_scan)
        buttons_hbox.addWidget(self.start_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_scan)
        self.cancel_button.setEnabled(False)
        buttons_hbox.addWidget(self.cancel_button)

        return group

    def get_scan_settings(self) -> FrequencyScanSettings:
        zaber_pos = None
        if self.zaber_set_pos_checkbox.isChecked():
            zaber_pos = float(self.zaber_pos_field.value())

        return FrequencyScanSettings(
            experiment=Experiment(
                sample_name=self.sample_name_field.text(),
                sample_temp=float(self.sample_temp_field.value()),
                gas_name=self.gas_name_field.text(),
                gas_width=float(self.gas_width_field.value()),
                backing_pressure=float(self.backing_pressure_field.value()),
                chamber_pressure=self.chamber_pressure_field.text(),
                mw_width=float(self.mw_width_field.value()),
            ),
            scan_parameters=ScanParameters(
                start_freq=float(self.start_freq_field.value()),
                end_freq=float(self.end_freq_field.value()),
                step_size=float(self.step_size_field.value()),
                scanning_speed=float(self.scanning_speed_field.value()),
                zaber_pos=zaber_pos,
                acq_num=int(self.acq_field.value())
            ),
            digitizer_settings=DigitizerSettings(
                resolution=int(self.resolution_field.value()),
                acq_window=int(self.acq_window_field.value()),
                apodization=self.apodization_field.currentText(),
            ),
            timing_settings=TimingSettings(
                rep_rate=int(self.rep_rate_field.value()),
                valve_mw_delay=int(self.valve_mw_delay_field.value()),
                spdt_width=self.spdt_width_field.value(),
                acq_delay=int(self.acq_delay_field.value())
            ),
            output_settings=OutputSettings(
                filename=self.output_folder_field.text(),
                location=self.directory_field.text(),
            ),
        )

    @Slot()
    def start_scan(self):
        settings = self.get_scan_settings()
        self.spec_controller.run_scan(settings)

    @Slot()
    def cancel_scan(self):
        self.spec_controller.cancel_operation()

    @Slot(bool, ScanType)
    def on_scanning(self, scanning: bool, scan_type: ScanType):
        if scanning:
            # Disable controls
            self.start_button.setEnabled(False)
            self.experiment_group.setEnabled(False)
            self.scan_settings_group.setEnabled(False)
            self.digitizer_group.setEnabled(False)
            self.timing_group.setEnabled(False)

            if scan_type == ScanType.FREQUENCY:
                self.cancel_button.setEnabled(True)
            else:
                self.cancel_button.setEnabled(False)
        else:
            # Reenable controls
            self.start_button.setEnabled(True)
            self.experiment_group.setEnabled(True)
            self.scan_settings_group.setEnabled(True)
            self.digitizer_group.setEnabled(True)
            self.timing_group.setEnabled(True)
            self.cancel_button.setEnabled(False)

    @Slot(GraphState)
    def on_update_graph(self, graph_state: GraphState):
        if graph_state.scan_type != ScanType.FREQUENCY:
            return

        if graph_state.fft_x:
            self.spectrum_x.extend(graph_state.fft_x)
            self.spectrum_y.extend(graph_state.fft_y)


        self.spectrum_plot.setData(self.spectrum_x, self.spectrum_y)

    @Slot(CavityTrackState)
    def on_update_cavityTrack(self, graph_state: CavityTrackState):
        if graph_state.scan_type != ScanType.FREQUENCY:
            return        

        if graph_state.cavityFreq:

            self.cavity_track_x.extend(graph_state.cavityFreq)
            self.cavity_track_y.extend(graph_state.cavityInt)

        self.cavity_track_plot.setData(self.cavity_track_x, self.cavity_track_y)
           


    @Slot(float)
    def on_zaber_position(self, position):
        if self.zaber_set_pos_checkbox.isChecked():
            return

        if position != -1 and not self.zaber_pos_field.hasFocus():
            self.zaber_pos_field.setValue(position)
            self.zaber_set_pos_checkbox.setEnabled(True)
        else:
            self.zaber_pos_field.setValue(0)
            self.zaber_set_pos_checkbox.setChecked(False)
            self.zaber_set_pos_checkbox.setEnabled(False)

    @Slot(bool)
    def on_zaber_set_pos_toggled(self, checked):
        self.zaber_pos_field.setEnabled(checked)

    def _populate_preset_dropdown(self):
        self.preset_combo.clear()
        if self.spec_controller.settings.scope_preset.presets:
            for _, preset in self.spec_controller.settings.scope_preset.presets.items():
                self.preset_combo.addItem(preset.name, preset)
        self.preset_combo.addItem("None")

    def _recall_preset(self):
        preset = self.preset_combo.currentData()
        if preset:
            self.spec_controller.spectrometer.oscilloscope_controller.recall_setup(
                preset.path, self.spec_controller.settings.scope_preset.root_path
            )
            self._populate_preset_dropdown()

    @Slot(object)
    def on_settings_updated(self, settings):
        self.spec_controller.settings = settings
        self._populate_preset_dropdown()

    @Slot()
    def on_browse_directory(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Directory", self.directory_field.text()
        )
        if folder:
            self.directory_field.setText(folder)
