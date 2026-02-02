from PySide6.QtWidgets import QWidget

# from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure


class GraphCanvas(QWidget):
    def __init__(self, width=5, height=5, dpi=100):
        super().__init__()
        figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = figure.add_subplot(111)
