import asyncio
from PySide6 import QtCore
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGroupBox,
)

from gui.spectrometer_controller import SpectrometerController


class StatusPanel(QWidget):
    def __init__(self, spectrometer: SpectrometerController):
        super().__init__()

        self.spectrometer = spectrometer
        self.device_circles = {}
        self.refresh_buttons = {}
        self.setup_ui()
        self.refresh_all_status()

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

        left_column = QWidget()
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
            status_label.setStyleSheet(
                "color: gray; font-size: 16px; font-weight: bold;"
            )
            self.device_circles[device_id] = status_label

            # Create row: Device name + Status indicator + Refresh button
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_widget.setLayout(row_layout)

            name_label = QLabel(display_name)
            row_layout.addWidget(name_label)
            row_layout.addStretch()

            # Status circle
            row_layout.addWidget(status_label)

            # Refresh button
            refresh_btn = QPushButton("🔄")
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
        self.update_circle(device_id, "gray")

        asyncio.create_task(self.refresh_device_async(device_id))

    async def refresh_device_async(self, device_id):
        try:
            success = await self.spectrometer.refresh_device(device_id)
        except Exception as e:
            success = False

        QtCore.QTimer.singleShot(
            100, lambda: self.update_device_status(device_id, success)
        )

    def update_circle(self, device_id, color):
        circle = self.device_circles[device_id]
        if circle:
            if color == "green":
                circle.setStyleSheet(
                    "color: #00AA00; font-size: 16px; font-weight: bold;"
                )
            elif color == "red":
                circle.setStyleSheet(
                    "color: #CC0000; font-size: 16px; font-weight: bold;"
                )
            else:
                circle.setStyleSheet("color: gray; font-size: 16px; font-weight: bold;")

    def update_device_status(self, device_id, success):
        self.update_circle(device_id, "green" if success else "red")
        self.refresh_buttons[device_id].setEnabled(True)

    def refresh_all_status(self):
        device_status = self.spectrometer.spectrometer.get_device_status()

        for device_id, is_initialized in device_status.items():
            self.update_circle(device_id, "green" if is_initialized else "red")
