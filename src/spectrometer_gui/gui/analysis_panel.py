from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFormLayout,
    QPushButton,
    QLineEdit,
)
from PySide6.QtGui import QFont, QCursor

import pyqtgraph as pg

from settings import Settings


class AnalysisPanel(QWidget):
    def __init__(self, settings: Settings, analysis_data=None):
        super().__init__()
        
        self.settings = settings

        if analysis_data is None:
            analysis_data = []

        self.analysis_data = analysis_data

        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left column
        left_column = QVBoxLayout()
        left_column_panel = QWidget()
        left_column_panel.setLayout(left_column)

        left_label = QLabel("Analysis")
        left_label.setFont(QFont("Arial", pointSize=24, weight=QFont.Weight.Bold))
        left_column.addWidget(left_label)

        form_panel = QWidget()
        form = QFormLayout()
        form_panel.setLayout(form)

        left_column.addWidget(form_panel)

        # threshold_label = QLabel("Automatically find peaks")
        # form.addRow(threshold_label)

        # self.threshold_field = QLineEdit("")
        # find_button = QPushButton("Find peaks")
        # form.addRow(self.threshold_field, find_button)

        left_column.addStretch(1)

        # Right column
        right_column = QVBoxLayout()
        right_column_panel = QWidget()
        right_column_panel.setLayout(right_column)
        right_column.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

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

            self.spectrum_plot = self.analysis_graph.plot(
                self.analysis_data.iloc[:, 0], 
                self.analysis_data.iloc[:, 1],
                pen = pg.mkPen(color="b", width=1),
                symbol='o' if self.settings.analysis.show_points else None,
                symbolSize=10,
                symbolBrush='b'
            )

    def set_data(self, df):
        self.analysis_data = df
        self.update_plot()

    def _create_analysis_graph(self) -> QWidget:
        self.analysis_graph = pg.PlotWidget(title="Spectrum")
        self.analysis_graph.setLabel("bottom", "Frequency (MHz)")
        self.analysis_graph.setLabel("left", "Relative Intensity (Volts)")
        self.analysis_graph.showGrid(x=True, y=True, alpha=0.3)
        self.analysis_graph.plotItem.getViewBox().setMouseEnabled(x=False, y=False)  # type: ignore
        self.analysis_graph.getPlotItem().layout.setContentsMargins(5, 0, 15, 10)  # type: ignore
        self.spectrum_plot = self.analysis_graph.plot()

        # Cursor
        cursor = QCursor(Qt.CursorShape.CrossCursor)
        self.analysis_graph.setCursor(cursor)

        # Crosshair lines
        self.crosshair_x = pg.InfiniteLine(angle=0, movable=False)
        self.crosshair_y = pg.InfiniteLine(angle=90, movable=False)
        self.analysis_graph.addItem(self.crosshair_x, ignore=True)
        self.analysis_graph.addItem(self.crosshair_y, ignore=True)

        self.proxy = pg.SignalProxy(self.analysis_graph.scene().sigMouseMoved, rateLimit=60, slot=self._update_crosshair)

        return self.analysis_graph

    def _update_crosshair(self, e):
        pos = e[0]
        if self.analysis_graph.sceneBoundingRect().contains(pos):
            mousePos = self.analysis_graph.getPlotItem().vb.mapSceneToView(pos)
            self.crosshair_x.setPos(mousePos.y())
            self.crosshair_y.setPos(mousePos.x())
