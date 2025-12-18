import asyncio

from PySide6 import QtCore, QtAsyncio
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from gui.spectrometer_controller import SpectrometerController


class CavitySearchPanel(QWidget):
    def __init__(self, spectrometer: SpectrometerController):
        super().__init__()

        self.spectrometer = spectrometer

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
        form_panel = QWidget()
        form = QFormLayout()
        form_panel.setLayout(form)

        left_column.addWidget(form_panel)

        start_freq_label = QLabel("Starting Frequency")
        start_freq_field = QLineEdit()
        form.addRow(start_freq_label, start_freq_field)

        step_size_label = QLabel("Step Size")
        self.step_size_field = QLineEdit("0.5")
        form.addRow(step_size_label, self.step_size_field)

        end_freq_label = QLabel("Ending Frequency")
        self.end_freq_field = QLineEdit("9000")
        form.addRow(end_freq_label, self.end_freq_field)

        start_button = QPushButton("Start")
        start_button.clicked.connect(lambda: asyncio.create_task(self.search_button()))
        left_column.addWidget(start_button)

        left_column.addStretch(1)

        # Right Column
        right_column = QVBoxLayout()
        right_column_panel = QWidget()
        right_column_panel.setLayout(right_column)

        right_column.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        right_image = QLabel()
        right_image.setPixmap(QPixmap("./src/gui/example_image.png"))
        right_column.addWidget(right_image)

        layout.addWidget(left_column_panel)
        layout.addWidget(right_column_panel)

        layout.setStretch(0, 1)
        layout.setStretch(1, 1)

    async def search_button(self):
        print("Starting cavity search from the GUI...")
        await asyncio.gather(
            self.spectrometer.run_search(
                int(self.end_freq_field.text()), float(self.step_size_field.text())
            )
        )
