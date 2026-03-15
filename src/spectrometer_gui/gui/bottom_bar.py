from __future__ import annotations
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QProgressBar

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

        self.setLayout(layout)

        # spectrometer.signal.device_status_changed.connect(self.on_device_status_changed)
        spectrometer.signal.progress.connect(self.set_status_elements)

    def set_status_elements(self, progress, text=None):
        if progress == -1:
            self.bottom_progress_bar.setRange(0, 0)
        else:
            self.bottom_progress_bar.setRange(0, 100)
            self.bottom_progress_bar.setValue(progress * 100)

        if text is not None:
            self.bottom_text.setText(text)
