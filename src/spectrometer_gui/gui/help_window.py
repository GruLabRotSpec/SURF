from pathlib import Path

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout,
    QLabel,
    QTextBrowser
)

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Help")

        self.help_path = Path("__file__").parent.parent / "docs" / "help.md"

        layout = QVBoxLayout()
        self.setLayout(layout)

        help_browser = QTextBrowser(openExternalLinks=True)
        help_browser.setMarkdown("The help file was not loaded.")

        if not self.help_path.exists():
            raise FileNotFoundError(f"Help file not found: {self.help_path}")

        with open(self.help_path, "r") as f:
            markdown = f.read()
            help_browser.setMarkdown(markdown)
    
        layout.addWidget(help_browser)