from PySide6.QtWidgets import QApplication, QLabel
from main_window import MainWindow

app = QApplication()

window = MainWindow(app)
window.show()

app.exec()
