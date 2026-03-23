from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure


class GraphCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)
