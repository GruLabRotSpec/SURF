from PySide6 import QtCore
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QDoubleSpinBox,
    QComboBox,
)

import pyqtgraph as pg

from gui.spectrometer_controller import SpectrometerController
from spectrometer import ScanType


class CavitySearchPanel(QWidget):
    def __init__(self, spectrometer: SpectrometerController):
        super().__init__()

        self.spec_controller = spectrometer
        self.spec_controller.signal.scanning.connect(self.on_scanning)

        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left Column
        left_column = QVBoxLayout()
        left_column_panel = QWidget()
        left_column_panel.setLayout(left_column)

        left_column.addStretch(1)

        left_label = QLabel("Cavity Search")
        left_label.setFont(QFont("Arial", pointSize=24, weight=QFont.Weight.Bold))
        left_column.addWidget(left_label)

        # Form
        self.form_panel = QWidget()
        form = QFormLayout()
        self.form_panel.setLayout(form)

        left_column.addWidget(self.form_panel)

        cavity_type_label = QLabel("Cavity Type")
        self.cavity_type_field = QComboBox()
        self.cavity_type_field.addItems(["Continuous", "Pulsed"])
        form.addRow(cavity_type_label, self.cavity_type_field)

        start_freq_label = QLabel("Starting Frequency")
        start_freq_field = QDoubleSpinBox()
        start_freq_field.setMinimum(8000)
        start_freq_field.setMaximum(18000)
        start_freq_field.setSingleStep(1000)
        start_freq_field.setDecimals(3)
        start_freq_field.setSuffix(" MHz")
        form.addRow(start_freq_label, start_freq_field)

        end_freq_label = QLabel("Ending Frequency")
        self.end_freq_field = QDoubleSpinBox()
        self.end_freq_field.setMinimum(8000)
        self.end_freq_field.setMaximum(18000)
        self.end_freq_field.setValue(9000)
        self.end_freq_field.setDecimals(3)
        self.end_freq_field.setSuffix(" MHz")
        form.addRow(end_freq_label, self.end_freq_field)

        zaber_speed_label = QLabel("Zaber Scanning Speed")
        self.zaber_speed_field = QDoubleSpinBox(
            maximum=5.00, decimals=2, suffix=" mm/s"
        )
        form.addRow(zaber_speed_label, self.zaber_speed_field)

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start_search)
        left_column.addWidget(start_button)
        self.start_button = start_button

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_search)
        cancel_button.setEnabled(False)
        left_column.addWidget(cancel_button)
        self.cancel_button = cancel_button

        left_column.addStretch(1)

        # Right Column
        right_column = QVBoxLayout()
        right_column_panel = QWidget()
        right_column_panel.setLayout(right_column)

        right_column.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        right_column.addWidget(self._create_spectrum_graph())

        layout.addWidget(left_column_panel)
        layout.addWidget(right_column_panel)

        layout.setStretch(0, 1)
        layout.setStretch(1, 1)

    def start_search(self):
        # Start search via controller (controller handles async internally)
        self.spec_controller.run_search(
            self.cavity_type_field.currentText(),
            int(self.end_freq_field.value()),
            float(1),  # Replace later
        )

    def cancel_search(self):
        self.spec_controller.cancel_operation()

    def on_scanning(self, scanning: bool, scan_type: ScanType):
        if scanning:
            self.start_button.setEnabled(False)
            self.form_panel.setEnabled(False)

            if scan_type == ScanType.CAVITY:
                self.cancel_button.setEnabled(True)
            else:
                self.cancel_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)
            self.form_panel.setEnabled(True)
            self.cancel_button.setEnabled(False)

    def _create_spectrum_graph(self) -> QWidget:
        self.spectrum_graph = pg.PlotWidget()
        self.spectrum_graph.showGrid(x=True, y=True, alpha=0.3)
        self.spectrum_graph.plotItem.getViewBox().setMouseEnabled(x=False, y=False)  # type: ignore
        self.spectrum_graph.getPlotItem().layout.setContentsMargins(5, 0, 15, 10)  # type: ignore
        self.spectrum_plot = self.spectrum_graph.plot(pen=pg.mkPen(color="b", width=1))
        return self.spectrum_graph
