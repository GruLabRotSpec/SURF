from PySide6 import QtCore
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


class FrequencyScanPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left Column
        left_column = QVBoxLayout()
        left_column_panel = QWidget()
        left_column_panel.setLayout(left_column)

        left_column.addStretch(1)

        left_label = QLabel("Frequency Scan")
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
        step_size_field = QLineEdit()
        form.addRow(step_size_label, step_size_field)

        end_freq_label = QLabel("Ending Frequency")
        end_freq_field = QLineEdit()
        form.addRow(end_freq_label, end_freq_field)

        start_button = QPushButton("Start")
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
