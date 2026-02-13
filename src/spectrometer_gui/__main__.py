from PySide6 import QtAsyncio
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow


def main():
    app = QApplication()

    window = MainWindow(app)
    window.show()

    QtAsyncio.run()


if __name__ == "__main__":
    main()
