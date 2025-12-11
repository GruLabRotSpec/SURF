from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication, QLabel

from spectrometer import Spectrometer
from gui.main_window import MainWindow


def main():
    spectrometer = Spectrometer()

    app = QApplication()

    window = MainWindow(app, spectrometer)
    window.show()

    QtAsyncio.run()


if __name__ == "__main__":
    main()
