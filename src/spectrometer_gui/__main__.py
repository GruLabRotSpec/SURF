from PySide6.QtWidgets import QApplication, QLabel

from spectrometer import Spectrometer
from gui.main_window import MainWindow


def main():
    spectrometer = Spectrometer()

    app = QApplication()

    window = MainWindow(app, spectrometer)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
