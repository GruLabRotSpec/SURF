from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLineEdit,
    QDoubleSpinBox,
)
from PySide6.QtCharts import QChartView, QChart, QLineSeries, QValueAxis
from PySide6.QtCore import Qt, QPointF

from gui.spectrometer_controller import SpectrometerController
from spectrometer import ScanType, GraphState


class FrequencyScanPanel(QWidget):
    def __init__(self, spectrometer: SpectrometerController):
        super().__init__()

        self.spec_xx = []
        self.spec_yy = []

        self.spectrometer = spectrometer

        self.spectrometer.signal.scanning.connect(self.on_scanning)
        self.spectrometer.signal.update_graph.connect(self.on_update_graph)
        self.spectrometer.signal.zaber_position.connect(self.on_zaber_position)

        layout = QVBoxLayout()
        self.setLayout(layout)

        top_row_hbox = QHBoxLayout()
        top_row_hbox.addWidget(self._create_scan_settings_panel())
        top_row_hbox.addWidget(self._create_experiment_params_panel())
        top_row_hbox.addWidget(self._create_config_panel())

        top_row_hbox.setStretch(0, 1)
        top_row_hbox.setStretch(1, 1)
        top_row_hbox.setStretch(2, 1)

        layout.addLayout(top_row_hbox)
        layout.setStretch(0, 1)

        layout.addWidget(self._create_spectrum_graph())
        layout.setStretch(1, 1)

        bottom_hbox = QHBoxLayout()
        bottom_hbox.addStretch()
        bottom_hbox.addWidget(self._create_cavity_track_graph(), 1)
        bottom_hbox.addWidget(self._create_scan_status_panel(), 1)

        layout.addLayout(bottom_hbox)
        layout.setStretch(2, 1)

        self.on_update_graph(GraphState(ScanType.FREQUENCY, [], [], 0, [], []))

    def _create_scan_settings_panel(self) -> QWidget:
        scan_settings_vbox = QVBoxLayout()

        scan_form = QFormLayout()
        self.scan_form_panel = QWidget()
        self.scan_form_panel.setLayout(scan_form)

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

        scan_settings_vbox.addWidget(self.scan_form_panel)

        buttons_hbox = QHBoxLayout()
        buttons_hbox.addStretch()

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_scan)
        buttons_hbox.addWidget(self.start_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_scan)
        self.cancel_button.setEnabled(False)
        buttons_hbox.addWidget(self.cancel_button)

        buttons_hbox.addStretch()
        scan_settings_vbox.addLayout(buttons_hbox)

        scan_settings_widget = QWidget()
        scan_settings_widget.setLayout(scan_settings_vbox)
        scan_settings_group = QGroupBox("Scan")
        scan_settings_group_layout = QHBoxLayout()
        scan_settings_group.setLayout(scan_settings_group_layout)
        scan_settings_group_layout.addWidget(scan_settings_widget)
        return scan_settings_group

    def _create_experiment_params_panel(self) -> QWidget:
        experiment_group = QGroupBox("Experiment parameters")

        experiment_form = QFormLayout()
        experiment_group.setLayout(experiment_form)

        sample_name_label = QLabel("Sample name")
        self.sample_name_field = QLineEdit()
        experiment_form.addRow(sample_name_label, self.sample_name_field)

        sample_temp_label = QLabel("Sample temp")
        self.sample_temp_field = QDoubleSpinBox(suffix=" C")
        experiment_form.addRow(sample_temp_label, self.sample_temp_field)

        gas_name_label = QLabel("Gas")
        self.gas_name_field = QLineEdit()
        experiment_form.addRow(gas_name_label, self.gas_name_field)

        gas_width_label = QLabel("Gas width")
        self.gas_width_field = QDoubleSpinBox(suffix=" μs")
        experiment_form.addRow(gas_width_label, self.gas_width_field)

        backing_pressure_label = QLabel("Backing pressure")
        self.backing_pressure_field = QDoubleSpinBox(
            value=15, maximum=25, suffix=" psi"
        )
        experiment_form.addRow(backing_pressure_label, self.backing_pressure_field)

        chamber_pressure_label = QLabel("Chamber pressure")
        self.chamber_pressure_field = QDoubleSpinBox(suffix=" torr")
        experiment_form.addRow(chamber_pressure_label, self.chamber_pressure_field)

        mw_width_label = QLabel("MW width")
        self.mw_width_field = QDoubleSpinBox(suffix=" μs")
        experiment_form.addRow(mw_width_label, self.mw_width_field)
        return experiment_group

    def _create_config_panel(self) -> QWidget:
        return QGroupBox("Config")

    def _create_spectrum_graph(self) -> QChartView:
        self.spectrum_graph = QChartView()
        self.spectrum_chart = QChart()
        self.spectrum_chart.setTitle("Spectrum")
        self.spectrum_chart.setTitleFont(
            QFont("Arial", pointSize=12, weight=QFont.Weight.Bold)
        )
        self.spectrum_chart.legend().setVisible(False)
        self.spectrum_graph.setChart(self.spectrum_chart)

        self.spectrum_series = QLineSeries()
        self.spectrum_x_axis = QValueAxis()
        self.spectrum_x_axis.setTitleText("Frequency (MHz)")
        self.spectrum_y_axis = QValueAxis()
        self.spectrum_y_axis.setTitleText("Relative Intensity (Volts)")
        self.spectrum_y_axis.setTitleFont(QFont("Arial", pointSize=8))
        self.spectrum_chart.addSeries(self.spectrum_series)
        self.spectrum_chart.addAxis(self.spectrum_x_axis, Qt.AlignmentFlag.AlignBottom)
        self.spectrum_chart.addAxis(self.spectrum_y_axis, Qt.AlignmentFlag.AlignLeft)
        self.spectrum_series.attachAxis(self.spectrum_x_axis)
        self.spectrum_series.attachAxis(self.spectrum_y_axis)
        return self.spectrum_graph

    def _create_cavity_track_graph(self) -> QChartView:
        self.cavity_track_graph = QChartView()
        self.cavity_track_chart = QChart()
        self.cavity_track_chart.setTitle("Cavity Track")
        self.cavity_track_chart.setTitleFont(
            QFont("Arial", pointSize=12, weight=QFont.Weight.Bold)
        )
        self.cavity_track_chart.legend().setVisible(False)
        self.cavity_track_graph.setChart(self.cavity_track_chart)

        self.cavity_track_series = QLineSeries()
        self.cavity_track_x_axis = QValueAxis()
        self.cavity_track_x_axis.setTitleText("Frequency (MHz)")
        self.cavity_track_y_axis = QValueAxis()
        self.cavity_track_y_axis.setTitleText("Relative Intensity (Volts)")
        self.cavity_track_y_axis.setTitleFont(QFont("Arial", pointSize=8))
        self.cavity_track_chart.addSeries(self.cavity_track_series)
        self.cavity_track_chart.addAxis(
            self.cavity_track_x_axis, Qt.AlignmentFlag.AlignBottom
        )
        self.cavity_track_chart.addAxis(
            self.cavity_track_y_axis, Qt.AlignmentFlag.AlignLeft
        )
        self.cavity_track_series.attachAxis(self.cavity_track_x_axis)
        self.cavity_track_series.attachAxis(self.cavity_track_y_axis)
        return self.cavity_track_graph

    def _create_scan_status_panel(self) -> QWidget:
        self.scan_status_group = QGroupBox("Scan Status")
        scan_status_form = QFormLayout()
        self.scan_status_group.setLayout(scan_status_form)
        self.scan_status_current_freq = QLabel("")
        self.scan_status_elapsed_time = QLabel("")
        self.scan_status_time_remaining = QLabel("")
        scan_status_form.addRow("Current Freq", self.scan_status_current_freq)
        scan_status_form.addRow("Elapsed Time", self.scan_status_elapsed_time)
        scan_status_form.addRow("Time Remaining", self.scan_status_time_remaining)
        export_button = QPushButton("Export Graphs")
        export_hbox = QHBoxLayout()
        export_hbox.addWidget(export_button)
        export_hbox.addStretch()
        scan_status_form.addRow("", export_hbox)
        return self.scan_status_group

    @Slot()
    def start_scan(self):
        start_pos = None
        if self.zaber_set_pos_checkbox.isChecked():
            start_pos = float(self.zaber_pos_field.value())
        self.spectrometer.run_scan(
            float(self.start_freq_field.value()),
            float(self.end_freq_field.value()),
            float(self.step_size_field.value()),
            start_pos,
        )

    @Slot()
    def cancel_scan(self):
        self.spectrometer.cancel_operation()

    @Slot(bool, ScanType)
    def on_scanning(self, scanning: bool, scan_type: ScanType):
        if scanning:
            self.start_button.setEnabled(False)
            self.scan_form_panel.setEnabled(False)

            if scan_type == ScanType.FREQUENCY:
                self.cancel_button.setEnabled(True)
            else:
                self.cancel_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)
            self.scan_form_panel.setEnabled(True)
            self.cancel_button.setEnabled(False)

    @Slot(GraphState)
    def on_update_graph(self, graph_state: GraphState):
        if graph_state.scan_type != ScanType.FREQUENCY:
            return

        if graph_state.fft_x:
            self.spec_xx.extend(graph_state.fft_x)
            self.spec_yy.extend(graph_state.fft_y)

        points = [
            QPointF(x, y) for x, y in zip(self.spec_xx, self.spec_yy, strict=False)
        ]
        self.spectrum_series.replace(points)

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
        if checked:
            self.zaber_pos_field.setEnabled(True)
        else:
            self.zaber_pos_field.setEnabled(False)
