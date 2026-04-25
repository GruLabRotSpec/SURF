from PySide6 import QtCore
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

        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left Column
        left_column = QVBoxLayout()
        left_column_panel = QWidget()
        left_column_panel.setLayout(left_column)

        left_column.addStretch(1)

        left_label = QLabel("Frequency Scan")
        left_label.setFont(QFont("Arial", pointSize=24, weight=QFont.Weight.Bold))
        left_column.addWidget(left_label)

        # Form
        self.form_panel = QWidget()
        form = QFormLayout()
        self.form_panel.setLayout(form)

        left_column.addWidget(self.form_panel)

        start_freq_label = QLabel("Starting Frequency")
        self.start_freq_field = QDoubleSpinBox(
            minimum=8000, maximum=18000, decimals=3, suffix=" MHz", value=10000
        )
        form.addRow(start_freq_label, self.start_freq_field)

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
        form.addRow(zaber_pos_label, zaber_pos_layout)

        step_size_label = QLabel("Freq Step Size")
        self.step_size_field = QDoubleSpinBox(
            minimum=0, maximum=1, value=0.5, singleStep=0.25, decimals=3, suffix=" MHz"
        )
        form.addRow(step_size_label, self.step_size_field)

        end_freq_label = QLabel("Ending Frequency")
        self.end_freq_field = QDoubleSpinBox(
            minimum=8000, maximum=18000, decimals=3, suffix=" MHz", value=10500
        )
        form.addRow(end_freq_label, self.end_freq_field)

        experiment_group = QGroupBox("Experiment parameters")

        experiment_form = QFormLayout()
        experiment_group.setLayout(experiment_form)

        experiment_info_label = QLabel(
            "These do not affect the spectrometer from the GUI"
        )
        experiment_form.addRow(experiment_info_label)

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

        left_column.addWidget(experiment_group)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_scan)
        left_column.addWidget(self.start_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_scan)
        self.cancel_button.setEnabled(False)
        left_column.addWidget(self.cancel_button)

        left_column.addStretch(1)

        # Right Column
        right_column = QVBoxLayout()
        right_column_panel = QWidget()
        right_column_panel.setLayout(right_column)

        right_column.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.chart_view = QChartView()
        self.chart = QChart()
        self.chart.setTitle("Spectrum")
        self.chart_view.setChart(self.chart)

        self.axes2_series = QLineSeries()
        self.axes2_x_axis = QValueAxis()
        self.axes2_x_axis.setTitleText("Frequency (MHz)")
        self.axes2_y_axis = QValueAxis()
        self.axes2_y_axis.setTitleText("Relative Intensity (Volts)")
        self.chart.addSeries(self.axes2_series)
        self.chart.addAxis(self.axes2_x_axis, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axes2_y_axis, Qt.AlignmentFlag.AlignLeft)
        self.axes2_series.attachAxis(self.axes2_x_axis)
        self.axes2_series.attachAxis(self.axes2_y_axis)

        right_column.addWidget(self.chart_view)

        layout.addWidget(left_column_panel)
        layout.addWidget(right_column_panel)

        layout.setStretch(0, 1)
        layout.setStretch(1, 1)

        self.on_update_graph(GraphState(ScanType.FREQUENCY, [], [], 0, [], []))

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
            self.form_panel.setEnabled(False)

            if scan_type == ScanType.FREQUENCY:
                self.cancel_button.setEnabled(True)
            else:
                self.cancel_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)
            self.form_panel.setEnabled(True)
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
        self.axes2_series.replace(points)

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
