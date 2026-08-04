from __future__ import annotations
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QProgressBar
from PySide6.QtCore import Slot
from gui.signal_enums import DeviceStatus
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
        self.scan_status_time_remaining = QLabel("Remaining: -")

        layout.addWidget(self.scan_status_current_freq)
        layout.addWidget(self.scan_status_elapsed_time)
        layout.addWidget(self.scan_status_time_remaining)

        # layout.setStretch(2, 1)
        layout.addStretch(5)

        self.status_circle = QLabel("●")
        self.status_circle.setStyleSheet(
            "color: gray; font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(self.status_circle)

        self.setLayout(layout)

        spectrometer.signal.progress.connect(self.set_status_elements)

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

    def set_scan_current_freq(self, freq: float):
        self.scan_status_current_freq.setText(f"Current Freq: {freq:.3f} MHz")

    def set_scan_elapsed_time(self, elapsed: str):
        self.scan_status_elapsed_time.setText(f"Elapsed: {elapsed}")

    def set_scan_time_remaining(self, remaining: str):
        self.scan_status_time_remaining.setText(f"Remaining: {remaining}")
