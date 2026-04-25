import asyncio
from pathlib import Path
from PySide6.QtCore import Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGroupBox,
)

from gui.spectrometer_controller import SpectrometerController, DeviceStatus
import contextlib


class StatusPanel(QWidget):
    def __init__(self, spectrometer: SpectrometerController):
        super().__init__()

        self.spectrometer = spectrometer
        self.device_circles = {}
        self.refresh_buttons = {}
        self._refresh_task: asyncio.Task | None = None
        self.setup_ui()

        # Signals
        self.spectrometer.signal.device_status_changed.connect(
            self.on_device_status_changed
        )

    def setup_ui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        left_column = QWidget()
        left_layout = QVBoxLayout()
        left_column.setLayout(left_layout)

        self.create_device_status_section(left_layout)

        right_column = QWidget()
        right_layout = QVBoxLayout()
        right_column.setLayout(right_layout)

        layout.addWidget(left_column)
        layout.addWidget(right_column)

        layout.setStretch(0, 1)
        layout.setStretch(1, 1)

    def create_device_status_section(self, parent_layout):
        status_group = QGroupBox("Device Status")
        status_layout = QFormLayout()

        status_group.setLayout(status_layout)

        # Device status rows
        devices = [
            ("zaber", "Zaber Controller"),
            ("oscilloscope", "Oscilloscope Controller"),
            ("valon", "Valon Controller"),
            ("switch", "Switch Controller"),
            ("delay_generator", "Delay Generator"),
            ("awg", "AWG Controller"),
        ]

        for device_id, display_name in devices:
            status_label = QLabel("●")
            self.device_circles[device_id] = status_label
            self.update_circle(device_id, DeviceStatus.CONNECTING)

            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_widget.setLayout(row_layout)

            name_label = QLabel(display_name)
            row_layout.addWidget(name_label)
            row_layout.addStretch()

            # Status circle
            row_layout.addWidget(status_label)

            # Refresh button
            refresh_btn = QPushButton()
            icon_path = str(Path(__file__).parent / "icons/refresh-cw.svg")
            refresh_btn.setIcon(QIcon(icon_path))
            refresh_btn.setToolTip("Refresh device connection")
            refresh_btn.setFixedSize(30, 30)
            refresh_btn.clicked.connect(
                lambda checked, dev=device_id: self.on_refresh_clicked(dev)
            )
            self.refresh_buttons[device_id] = refresh_btn
            row_layout.addWidget(refresh_btn)

            status_layout.addRow(row_widget)

        parent_layout.addWidget(status_group)

    def on_refresh_clicked(self, device_id):
        self.refresh_buttons[device_id].setEnabled(False)
        if self._refresh_task:
            self._refresh_task.cancel()
        self._refresh_task = asyncio.create_task(self.refresh_device_async(device_id))

    async def refresh_device_async(self, device_id):
        with contextlib.suppress(Exception):
            await self.spectrometer.refresh_device(device_id)

        self.refresh_buttons[device_id].setEnabled(True)

    def update_circle(self, device_id: str, status: DeviceStatus):
        circle = self.device_circles[device_id]
        if circle:
            if status == DeviceStatus.ONLINE:
                circle.setStyleSheet(
                    "color: #00AA00; font-size: 16px; font-weight: bold;"
                )
            elif status == DeviceStatus.OFFLINE:
                circle.setStyleSheet(
                    "color: #CC0000; font-size: 16px; font-weight: bold;"
                )
            else:  # CONNECTING
                circle.setStyleSheet("color: gray; font-size: 16px; font-weight: bold;")

    @Slot(str, DeviceStatus)
    def on_device_status_changed(self, device_id, status):
        self.update_circle(device_id, status)
