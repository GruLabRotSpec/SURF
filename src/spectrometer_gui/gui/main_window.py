from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QFileDialog,
)

from gui.settings_window import SettingsWindow
from gui.about_window import AboutWindow

from gui.frequency_scan_panel import FrequencyScanPanel
from gui.cavity_search_panel import CavitySearchPanel
from gui.control_panel import ControlPanel
from gui.analysis_panel import AnalysisPanel
from gui.bottom_bar import BottomBarPanel
from gui.spectrometer_controller import SpectrometerController

from spectrometer import Spectrometer


class MainWindow(QMainWindow):
    def __init__(self, app, spectrometer: Spectrometer):
        super().__init__()

        self.app = app
        self.setWindowTitle("Gru GUI")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        self.setLayout(layout)

        self.menu_bar = self.menuBar()
        self.setup_menu_bar()

        bottom_bar_panel = BottomBarPanel()

        controller = SpectrometerController(spectrometer, bottom_bar_panel)

        frequency_scan = FrequencyScanPanel(controller)
        cavity_search = CavitySearchPanel(controller)
        control_panel = ControlPanel()
        analysis_panel = AnalysisPanel()

        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(frequency_scan, "Frequency Scan")
        self.tab_widget.addTab(cavity_search, "Cavity Search")
        self.tab_widget.addTab(control_panel, "Control")
        self.tab_widget.addTab(analysis_panel, "Analysis")

        layout.addWidget(self.tab_widget)
        layout.addWidget(bottom_bar_panel)

    def setup_menu_bar(self):
        # File Menu
        file_menu = self.menu_bar.addMenu("&File")

        open_spectra_action = file_menu.addAction(
            "Open emission spectra for analysis..."
        )
        open_spectra_action.triggered.connect(self.open_spectra)

        quit_action = file_menu.addAction("Show Error")
        quit_action.triggered.connect(self.show_error)

        error_action = file_menu.addAction("Quit")
        error_action.triggered.connect(self.quit_app)

        # Edit Menu
        edit_menu = self.menu_bar.addMenu("&Edit")

        settings_action = edit_menu.addAction("Settings")
        settings_action.triggered.connect(self.show_settings)

        # View Menu
        self.menu_bar.addMenu("&View")

        # Help Menu
        help_menu = self.menu_bar.addMenu("&Help")

        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def quit_app(self):
        self.app.quit()

    def open_spectra(self):
        selection = QMessageBox.warning(
            self,
            "Warning",
            "If an emission spectra is already open for analysis, it will be overwritten. Do you want to continue?",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
        )

        if selection == QMessageBox.StandardButton.Ok:
            if filename:
                filename, _ = QFileDialog.getOpenFileName(
                    self, "Open emission spectra", "C:/", "(*.csv)"
                )
                try:
                    with open(filename) as file:
                        # Replace later to send data to graph element on analysis panel
                        print(file.read())
                except:
                    QMessageBox.critical(
                        self,
                        "File Open Error",
                        "Unable to open the file.",
                        QMessageBox.StandardButton.Ok,
                    )

    def show_error(self):
        QMessageBox.critical(
            self,
            "Critical Error",
            "You triggered a Critical Error!",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Abort,
        )

    def show_settings(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def show_about(self):
        self.about_window = AboutWindow()
        self.about_window.show()
