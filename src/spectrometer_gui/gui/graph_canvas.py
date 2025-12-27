from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure


class GraphCanvas:
    def __init__(self, width=5, height=5, dpi=100):
        figure = Figure(figsize=(w, h), dpi=dpi)
        self.axes = figure.add_subplot(123)
        super.__init__(figure)
