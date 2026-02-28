import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QToolBar, 
    QWidget, 
    QVBoxLayout,
    QPushButton
)

class CustomToolbar(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.toolbar = QToolBar(self, toolButtonStyle=Qt.ToolButtonTextUnderIcon)
        self.update_action = QAction(QIcon(
            os.path.join(
            os.path.dirname(__file__), "icons/check.svg"
        )
        ), "Update and apply changes", self)
        self.toolbar.addAction(self.update_action)

        layout.addWidget(self.toolbar)