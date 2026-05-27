import asyncio
from pathlib import Path
from PySide6 import QtCore
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QFileDialog,
)

import pandas as pd

from gui.settings_window import SettingsWindow
from gui.help_window import HelpWindow
from gui.about_window import AboutWindow

from gui.broadband_panel import BroadbandPanel
from gui.frequency_scan_panel import FrequencyScanPanel
from gui.cavity_search_panel import CavitySearchPanel
from gui.control_panel import ControlPanel
from gui.analysis_panel import AnalysisPanel
from gui.status_panel import StatusPanel
from gui.bottom_bar import BottomBarPanel
from gui.spectrometer_controller import SpectrometerController

from settings import load_settings
from config import load_config, save_config
from gui.theme import apply_theme


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.settings_path = Path("./settings.toml")  # Change path later
        self.settings = load_settings(self.settings_path)
        apply_theme(self.settings.theme)
        self.config = load_config(
            Path(__file__).parent.parent / "defaults" / "default_config.toml"
        )

        self.setWindowTitle("Gru GUI")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        self.setLayout(layout)

        self.menu_bar = self.menuBar()
        self.setup_menu_bar()

        self.spec_controller = SpectrometerController(
            self.settings, self.config, self.settings_path
        )

        bottom_bar_panel = BottomBarPanel(self.spec_controller)
        status_panel = StatusPanel(self.spec_controller)
        broadband_panel = BroadbandPanel()
        frequency_scan = FrequencyScanPanel(self.spec_controller)
        cavity_search = CavitySearchPanel(self.spec_controller)
        control_panel = ControlPanel(self.spec_controller)
        self.analysis_panel = AnalysisPanel()

        status_panel.signal_status_changed.connect(
            bottom_bar_panel.set_spectrometer_status
        )

        self.tab_widget = QTabWidget(self)
        self.tab_widget.addTab(status_panel, "Status")
        self.tab_widget.addTab(broadband_panel, "Broadband")
        self.tab_widget.addTab(frequency_scan, "Frequency Scan")
        self.tab_widget.addTab(cavity_search, "Cavity Search")
        self.tab_widget.addTab(control_panel, "Control")
        self.tab_widget.addTab(self.analysis_panel, "Analysis")

        layout.addWidget(self.tab_widget)
        layout.addWidget(bottom_bar_panel)

        # This runs the first init after QtAsync gets loaded
        QtCore.QTimer.singleShot(
            100,
            lambda: asyncio.create_task(self.spec_controller.initialize_all_devices()),
        )

    def setup_menu_bar(self):
        # File Menu
        file_menu = self.menu_bar.addMenu("&File")

        open_config_action = file_menu.addAction("&Open control options from file...")
        open_config_action.setShortcut(QKeySequence.StandardKey.Open)
        open_config_action.triggered.connect(self.open_config)

        open_spectra_action = file_menu.addAction(
            "Open &emission spectra for analysis..."
        )
        open_spectra_action.triggered.connect(self.open_spectra)

        file_menu.addSeparator()

        save_config_action = file_menu.addAction("&Save control options to file...")
        save_config_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_config_action.triggered.connect(self.save_config)

        file_menu.addSeparator()

        quit_action = file_menu.addAction("&Quit")
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.setStatusTip("Quit the application")
        quit_action.triggered.connect(self.quit_app)

        # Edit Menu
        edit_menu = self.menu_bar.addMenu("&Edit")

        settings_action = edit_menu.addAction("&Settings")
        settings_action.triggered.connect(self.show_settings)

        # View Menu
        view_menu = self.menu_bar.addMenu("&View")

        fullscreen_action = view_menu.addAction("&Fullscreen")
        fullscreen_action.setShortcut(QKeySequence.StandardKey.FullScreen)
        fullscreen_action.setCheckable(True)
        fullscreen_action.triggered.connect(self.view_fullscreen)

        # Help Menu
        help_menu = self.menu_bar.addMenu("&Help")

        help_action = help_menu.addAction("&Help")
        help_action.setShortcut(QKeySequence.StandardKey.HelpContents)
        help_action.triggered.connect(self.show_help)

        about_action = help_menu.addAction("&About")
        about_action.triggered.connect(self.show_about)

    def open_config(self):
        dialog = QFileDialog()

        filename, _ = dialog.getOpenFileName(
            self,
            "Open Control Options from File",
            "",
            "GruGUI control options file (*.toml)",
        )

        if filename:
            self.config = load_config(Path(filename))
            self.spec_controller.set_config(self.config)
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Please select a valid control options file to open.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )

    def save_config(self):
        dialog = QFileDialog()

        filename, _ = dialog.getSaveFileName(
            self,
            "Save Control Options to File",
            "",
            "GruGUI control options file (*.toml)",
        )

        if filename:
            save_config(Path(filename), self.spec_controller.config)
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Please select a valid filename to save the control options file.",
                QMessageBox.StandardButton.Ok,
            )

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
            filename, _ = QFileDialog.getOpenFileName(
                self, "Open emission spectra", "C:/", "(*.csv)"
            )

            if filename:
                try:
                    df = pd.read_csv(filename)
                    self.analysis_panel.set_data(df)
                    print(df)
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "File Open Error",
                        f"Unable to open the file: {e}",
                        QMessageBox.StandardButton.Ok,
                    )

    def show_settings(self):
        self.settings_window = SettingsWindow(self.settings, self.settings_path)
        self.settings_window.settings_updated.connect(
            self.spec_controller.signal.settings_updated
        )
        self.settings_window.show()

    def view_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_help(self):
        self.help_window = HelpWindow()
        self.help_window.show()

    def show_about(self):
        self.about_window = AboutWindow()
        self.about_window.show()

    def closeEvent(self, event):
        print("Preparing to quit...")

        if self.spec_controller.current_task:
            quit_selection = QMessageBox.warning(
                self,
                "Quit During Task",
                "Quit and cancel the current task? Unsaved changes will be lost.",
                QMessageBox.StandardButton.Cancel | QMessageBox.StandardButton.Ok,
            )

            if quit_selection == QMessageBox.StandardButton.Ok:
                # Cleanup and cancel running tasks
                self.spec_controller.cancel_operation()

                event.accept()
            else:
                print("Quit cancelled")
                event.ignore()
