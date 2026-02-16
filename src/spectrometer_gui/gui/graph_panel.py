from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from matplotlib.backends.backend_qt import NavigationToolbar2QT as NaviToolbar

from gui.graph_canvas import GraphCanvas

import pandas as pd

class GraphPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.graph = GraphCanvas()
        layout.addWidget(self.graph)

        toolbar = NaviToolbar(self.graph, self)
        layout.addWidget(toolbar)

