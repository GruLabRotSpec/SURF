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

        self.bottom_text = QLabel("Idle, ready to scan")
        layout.addWidget(self.bottom_text)

        layout.setStretch(1, 1)

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
        if status == DeviceStatus.ONLINE:
            self.status_circle.setStyleSheet(
                "color: #00AA00; font-size: 16px; font-weight: bold;"
            )
        elif status == DeviceStatus.OFFLINE:
            self.status_circle.setStyleSheet(
                "color: #CC0000; font-size: 16px; font-weight: bold;"
            )
        else:
            self.status_circle.setStyleSheet(
                "color: gray; font-size: 16px; font-weight: bold;"
            )

    @Slot(float, str)
    def set_status_elements(self, progress, text=None):
        if progress == -1:
            self.bottom_progress_bar.setRange(0, 0)
        else:
            self.bottom_progress_bar.setRange(0, 100)
            self.bottom_progress_bar.setValue(progress * 100)

        if text is not None:
            self.bottom_text.setText(text)
