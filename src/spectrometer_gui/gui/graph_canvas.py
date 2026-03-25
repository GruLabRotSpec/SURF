from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure


class GraphCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=8, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.figure.subplots_adjust(hspace=0.4)
        self.axes1 = self.figure.add_subplot(211)
        self.axes2 = self.figure.add_subplot(212)
        super().__init__(self.figure)
