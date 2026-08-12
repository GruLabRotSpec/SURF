from __future__ import annotations
from datetime import timedelta

from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QProgressBar
from PySide6.QtCore import QTimer, Slot
from gui.signal_enums import DeviceStatus, ExperimentProgress
import typing

if typing.TYPE_CHECKING:
    from gui.spectrometer_controller import SpectrometerController


class BottomBarPanel(QWidget):
    def __init__(self, spectrometer: SpectrometerController):
        super().__init__()

        layout = QHBoxLayout()

        self.bottom_progress_bar = QProgressBar(maximum=1, textVisible=False)
        self.bottom_progress_bar.setValue(1)
        layout.addWidget(self.bottom_progress_bar)

        self.status_text = QLabel("Idle")
        layout.addWidget(self.status_text)

        self.divider0 = QLabel("|")
        self.divider0.setStyleSheet("color: gray;")
        layout.addWidget(self.divider0)

        self.scan_status_current_freq = QLabel("Current Freq: -")
        self.scan_status_elapsed_time = QLabel("Elapsed: -")
        self.scan_status_time_remaining = QLabel("Estimated Remaining: -")

        layout.addWidget(self.scan_status_current_freq)
        layout.addWidget(self.scan_status_elapsed_time)
        layout.addWidget(self.scan_status_time_remaining)

        # layout.setStretch(2, 1)
        layout.addStretch(5)

        self.elapsed_timer = QTimer(self)
        self.elapsed_timer.setInterval(1000)
        self.elapsed_timer.timeout.connect(self.update_elapsed_time)
        self.current_elapsed_seconds: int | None = None
        self.current_remaining_seconds: int | None = None

        self.status_circle = QLabel("●")
        self.status_circle.setStyleSheet(
            "color: gray; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.status_circle)

        self.setLayout(layout)

        spectrometer.signal.progress.connect(self.set_status_elements)
        spectrometer.signal.detailed_progress.connect(self.set_detailed_status_elements)
        spectrometer.search_signals.detailed_progress.connect(self.set_detailed_status_elements)
        spectrometer.signal.scanning.connect(self.on_scan_state_changed)

    def on_scan_state_changed(self, scanning: bool, scan_type):
        if not scanning and self.elapsed_timer.isActive():
            self.elapsed_timer.stop()

    @Slot(DeviceStatus)
    def set_spectrometer_status(self, status: DeviceStatus):
        match status:
            case DeviceStatus.ONLINE:
                self.status_circle.setStyleSheet(
                    "color: #00AA00; font-size: 16px; font-weight: bold;"
                )
                self.status_circle.setToolTip("Spectrometer online")
            case DeviceStatus.OFFLINE:
                self.status_circle.setStyleSheet(
                    "color: #CC0000; font-size: 16px; font-weight: bold;"
                )
                self.status_circle.setToolTip("Spectrometer offline")
            case DeviceStatus.CONNECTING:
                self.status_circle.setStyleSheet(
                    "color: gray; font-size: 16px; font-weight: bold;"
                )
                self.status_circle.setToolTip("Connecting")

    @Slot(float, str)
    def set_status_elements(self, progress, text=None):
        if progress == -1:
            self.bottom_progress_bar.setRange(0, 0)
        else:
            self.bottom_progress_bar.setRange(0, 100)
            self.bottom_progress_bar.setValue(progress * 100)

        if text is not None:
            self.status_text.setText(text)

    @Slot(ExperimentProgress)
    def set_detailed_status_elements(self, progress: ExperimentProgress):
        self.set_scan_current_freq(progress.current_freq)
        self.current_elapsed_seconds = self._parse_time_string(progress.elapsed_time)
        self.current_remaining_seconds = self._parse_time_string(progress.time_remaining)
        self.set_scan_elapsed_time(progress.elapsed_time)
        self.set_scan_time_remaining(progress.time_remaining)
        if not self.elapsed_timer.isActive():
            self.elapsed_timer.start()

    def update_elapsed_time(self):
        if self.current_elapsed_seconds is None:
            return

        self.current_elapsed_seconds += 1
        if self.current_remaining_seconds is not None:
            self.current_remaining_seconds = max(self.current_remaining_seconds - 1, 0)

        new_elapsed = str(timedelta(seconds=self.current_elapsed_seconds)).zfill(8)
        new_remaining = (
            str(timedelta(seconds=self.current_remaining_seconds)).zfill(8)
            if self.current_remaining_seconds is not None
            else "-"
        )

        self.set_scan_elapsed_time(new_elapsed)
        self.set_scan_time_remaining(new_remaining)

    def _parse_time_string(self, time_string: str) -> int | None:
        if not time_string or time_string == "-":
            return None

        parts = time_string.split(":")
        if len(parts) != 3:
            return None

        try:
            hours, minutes, seconds = map(int, parts)
            return hours * 3600 + minutes * 60 + seconds
        except ValueError:
            return None

    def set_scan_current_freq(self, freq: float):
        self.scan_status_current_freq.setText(f"Current Freq: {freq:.3f} MHz")

    def set_scan_elapsed_time(self, elapsed: str):
        self.scan_status_elapsed_time.setText(f"Elapsed: {elapsed}")

    def set_scan_time_remaining(self, remaining: str):
        self.scan_status_time_remaining.setText(f"Estimated Remaining: {remaining}")
