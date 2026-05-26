from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QTextBrowser
)
from PySide6.QtGui import QFont


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("About")

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        name_label = QLineEdit("SURF", readOnly=True, alignment=QtCore.Qt.AlignmentFlag.AlignCenter, frame=False)
        name_label.setFont(QFont("Arial", pointSize=16, weight=QFont.Weight.Bold))
        layout.addWidget(name_label)

        name_label = QLineEdit("Version: <unknown>", readOnly=True, alignment=QtCore.Qt.AlignmentFlag.AlignCenter, frame=False)
        name_label.setFont(QFont("Arial", pointSize=12))
        layout.addWidget(name_label)

        description_browser = QTextBrowser()
        description_browser.setMarkdown("Spectroscopy User and Research Framework (SURF) is a GUI for controlling a FTMW spectrometer.")
        layout.addWidget(description_browser)

        layout.addStretch(1)

