from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from matplotlib.backends.backend_qt import NavigationToolbar2QT as NaviToolbar

from gui.graph_canvas import GraphCanvas


class GraphPanel(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        graph = GraphCanvas()
        layout.addWidget(graph)

        toolbar = NaviToolbar(graph, self)
        layout.addWidget(toolbar)
