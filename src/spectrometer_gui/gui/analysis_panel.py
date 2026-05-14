from PySide6 import QtCore
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFormLayout,
    QPushButton,
    QLineEdit,
)
from PySide6.QtGui import QFont

import pyqtgraph as pg


class AnalysisPanel(QWidget):
    def __init__(self, analysis_data=None):
        super().__init__()

        if analysis_data is None:
            analysis_data = []

        self.analysis_data = analysis_data

        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left column
        left_column = QVBoxLayout()
        left_column_panel = QWidget()
        left_column_panel.setLayout(left_column)

        left_column.addStretch(1)

        left_label = QLabel("Analysis")
        left_label.setFont(QFont("Arial", pointSize=24, weight=QFont.Weight.Bold))
        left_column.addWidget(left_label)

        form_panel = QWidget()
        form = QFormLayout()
        form_panel.setLayout(form)

        left_column.addWidget(form_panel)

        threshold_label = QLabel("Automatically find peaks")
        form.addRow(threshold_label)

        self.threshold_field = QLineEdit("")
        find_button = QPushButton("Find peaks")
        form.addRow(self.threshold_field, find_button)

        # Right column
        right_column = QVBoxLayout()
        right_column_panel = QWidget()
        right_column_panel.setLayout(right_column)
        right_column.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # self.graph_panel = GraphPanel()
        right_column.addWidget(self._create_analysis_graph())

        layout.addWidget(left_column_panel)
        layout.addWidget(right_column_panel)

        layout.setStretch(0, 1)
        layout.setStretch(1, 3)

    def show_event(self, event):
        super().showEvent(event)

        self.update_plot()

    def update_plot(self):
        if not self.analysis_data.empty:
            print(self.analysis_data)
            self.spectrum_plot.setData(self.analysis_data.iloc[:, 0], self.analysis_data.iloc[:, 1])

    def set_data(self, df):
        self.analysis_data = df
        self.update_plot()

    def _create_analysis_graph(self) -> QWidget:
        self.analysis_graph = pg.PlotWidget(title="Spectrum")
        self.analysis_graph.setLabel("bottom", "Frequency (MHz)")
        self.analysis_graph.setLabel("left", "Relative Intensity (Volts)")
        self.analysis_graph.showGrid(x=True, y=True, alpha=0.3)
        self.analysis_graph.plotItem.getViewBox().setMouseEnabled(x=True, y=True)  # type: ignore
        self.analysis_graph.getPlotItem().layout.setContentsMargins(5, 0, 15, 10)  # type: ignore
        self.spectrum_plot = self.analysis_graph.plot(pen=pg.mkPen(color="b", width=1))
        return self.analysis_graph
