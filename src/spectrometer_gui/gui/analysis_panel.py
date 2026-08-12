from pathlib import Path

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
        self.analysis_filename = None
        self.selected_peaks: list[tuple[float, float]] = []

        layout = QVBoxLayout()
        self.setLayout(layout)

        title_label = QLabel("Analysis")
        title_label.setFont(QFont("Arial", pointSize=24, weight=QFont.Weight.Bold))
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title_label)

        layout.addWidget(self._create_analysis_graph(), stretch=1)

        self.coord_label = QLabel("x: -, y: -")
        self.coord_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.coord_label)

        self.selected_peak_label = QLabel("Selected peaks: -")
        self.selected_peak_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.selected_peak_label)

        self.peak_separation_label = QLabel("Separation: -")
        self.peak_separation_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.peak_separation_label)

        self.peak_average_label = QLabel("Average: -")
        self.peak_average_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.peak_average_label)

        self.peak_fwhm_label = QLabel("FWHM: -")
        self.peak_fwhm_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.peak_fwhm_label)

        self.clear_peaks_button = QPushButton("Clear selected peaks")
        self.clear_peaks_button.clicked.connect(self.clear_selected_peaks)
        layout.addWidget(self.clear_peaks_button)

    def show_event(self, event):
        super().showEvent(event)

        self.update_plot()

    def update_plot(self):
        if not self.analysis_data.empty:
            print(self.analysis_data)

            self.spectrum_plot.clear()
            self.spectrum_plot.setData(
                self.analysis_data.iloc[:, 0],
                self.analysis_data.iloc[:, 1],
                pen=pg.mkPen(color="b", width=1),
                symbol='o' if self.settings.analysis.show_points else None,
                symbolSize=10,
                symbolBrush='b',
            )

    def set_data(self, df, filename: str | None = None):
        self.analysis_data = df
        if filename:
            self.analysis_filename = Path(filename).stem
            self.analysis_graph.setTitle(self.analysis_filename)
        self.update_plot()

    def on_settings_updated(self, settings: Settings):
        self.settings = settings
        self.analysis_graph.showGrid(
            x=self.settings.analysis.show_grid,
            y=self.settings.analysis.show_grid,
            alpha=0.3,
        )
        self.crosshair_x.setVisible(self.settings.analysis.show_crosshair)
        self.crosshair_y.setVisible(self.settings.analysis.show_crosshair)
        self.update_plot()

    def _create_analysis_graph(self) -> QWidget:
        title = self.analysis_filename or "Spectrum"
        self.analysis_graph = pg.PlotWidget(title=title)
        self.analysis_graph.setLabel("bottom", "Frequency (MHz)")
        self.analysis_graph.setLabel("left", "Relative Intensity (Volts)")
        self.analysis_graph.showGrid(x=self.settings.analysis.show_grid, y=self.settings.analysis.show_grid, alpha=0.3)
        self.analysis_graph.plotItem.getViewBox().setMouseEnabled(x=False, y=False)  # type: ignore
        self.analysis_graph.getPlotItem().layout.setContentsMargins(5, 0, 15, 10)  # type: ignore
        self.spectrum_plot = self.analysis_graph.plot()
        self.selected_peak_plot = self.analysis_graph.plot(
            pen=None,
            symbol='o',
            symbolSize=12,
            symbolBrush='r',
            symbolPen=pg.mkPen(color='r', width=2),
        )

        # Cursor
        cursor = QCursor(Qt.CursorShape.CrossCursor)
        self.analysis_graph.setCursor(cursor)

        # Crosshair lines
        self.crosshair_x = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(color='k', width=1))
        self.crosshair_y = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(color='k', width=1))
        self.analysis_graph.addItem(self.crosshair_x, ignore=True)
        self.analysis_graph.addItem(self.crosshair_y, ignore=True)
        self.crosshair_x.setVisible(self.settings.analysis.show_crosshair)
        self.crosshair_y.setVisible(self.settings.analysis.show_crosshair)

        self.proxy = pg.SignalProxy(self.analysis_graph.scene().sigMouseMoved, rateLimit=60, slot=self._update_crosshair)
        self.analysis_graph.scene().sigMouseClicked.connect(self._on_mouse_clicked)

        return self.analysis_graph

    def _update_crosshair(self, e):
        pos = e[0]
        if self.analysis_graph.sceneBoundingRect().contains(pos):
            mousePos = self.analysis_graph.getPlotItem().vb.mapSceneToView(pos)
            self.crosshair_x.setPos(mousePos.y())
            self.crosshair_y.setPos(mousePos.x())
            self.coord_label.setText(f"x: {mousePos.x():.3f}, y: {mousePos.y():.3f}")

    def _on_mouse_clicked(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        pos = event.scenePos()
        if not self.analysis_graph.sceneBoundingRect().contains(pos):
            return

        mouse_point = self.analysis_graph.getPlotItem().vb.mapSceneToView(pos)
        x = mouse_point.x()
        y = mouse_point.y()

        if self.analysis_data.empty:
            return

        x_values = self.analysis_data.iloc[:, 0].to_numpy()
        y_values = self.analysis_data.iloc[:, 1].to_numpy()

        best_index = int((abs(x_values - x)).argmin())
        peak_x = float(x_values[best_index])
        peak_y = float(y_values[best_index])
        self._add_selected_peak(peak_x, peak_y)

    def _add_selected_peak(self, x: float, y: float):
        self.selected_peaks.append((x, y))
        if len(self.selected_peaks) > 2:
            self.selected_peaks.pop(0)

        self._update_peak_labels()
        self._update_selected_peak_plot()

    def _update_selected_peak_plot(self):
        if not self.selected_peaks:
            self.selected_peak_plot.setData([], [])
            return

        x_values = [peak_x for peak_x, _ in self.selected_peaks]
        y_values = [peak_y for _, peak_y in self.selected_peaks]
        self.selected_peak_plot.setData(x_values, y_values)

    def clear_selected_peaks(self):
        self.selected_peaks = []
        self._update_selected_peak_plot()
        self._update_peak_labels()

    def _compute_fwhm(self, peak_x: float, peak_y: float) -> float | None:
        x_values = self.analysis_data.iloc[:, 0].to_numpy()
        y_values = self.analysis_data.iloc[:, 1].to_numpy()

        half_max = peak_y / 2.0
        left_mask = x_values < peak_x
        right_mask = x_values > peak_x

        left_x = x_values[left_mask]
        left_y = y_values[left_mask]
        right_x = x_values[right_mask]
        right_y = y_values[right_mask]

        if left_x.size == 0 or right_x.size == 0:
            return None

        left_index = (abs(left_y - half_max)).argmin()
        right_index = (abs(right_y - half_max)).argmin()

        left_x_at_hm = float(left_x[left_index])
        right_x_at_hm = float(right_x[right_index])

        return abs(right_x_at_hm - left_x_at_hm)

    def _update_peak_labels(self):
        if not self.selected_peaks:
            self.selected_peak_label.setText("Selected peaks: -")
            self.peak_separation_label.setText("Separation: -")
            self.peak_fwhm_label.setText("FWHM: -")
            return

        peaks_text = ", ".join(
            [f"{peak_x:.3f}" for peak_x, _ in self.selected_peaks]
        )
        self.selected_peak_label.setText(f"Selected peaks: {peaks_text}")

        if len(self.selected_peaks) == 2:
            separation = abs(self.selected_peaks[1][0] - self.selected_peaks[0][0])
            self.peak_separation_label.setText(
                f"Separation: {separation:.3f} MHz"
            )
            average = sum(peak_x for peak_x, _ in self.selected_peaks) / 2.0
            self.peak_average_label.setText(f"Average: {average:.3f} MHz")
        else:
            self.peak_separation_label.setText("Separation: -")
            self.peak_average_label.setText("Average: -")

        peak_x, peak_y = self.selected_peaks[-1]
        fwhm = self._compute_fwhm(peak_x, peak_y)
        if fwhm is not None:
            self.peak_fwhm_label.setText(f"FWHM: {fwhm:.3f} MHz")
        else:
            self.peak_fwhm_label.setText("FWHM: -")
