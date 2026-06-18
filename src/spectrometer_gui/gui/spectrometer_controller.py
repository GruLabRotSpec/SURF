import asyncio
import traceback
import threading

from config import Config
from gui.signal_enums import DeviceStatus
from PySide6.QtCore import QObject, QTimer, Signal
from settings import Settings
from spectrometer import GraphState, CavityGraphState, ScanType, Spectrometer


class ScanSignals(QObject):
    device_status_changed = Signal(str, DeviceStatus)  # device_id, DeviceStatus
    progress = Signal(float, str)
    scanning = Signal(bool, ScanType)
    update_graph = Signal(GraphState)
    zaber_position = Signal(float)  # position in mm, or -1 on error
    settings_updated = Signal(object)  # Settings


class SearchSignals(QObject):
    update_graph = Signal(CavityGraphState)


class SpectrometerController(QObject):
    def __init__(self, settings: Settings, config: Config, settings_path=None):
        super().__init__()
        self.spectrometer = Spectrometer(settings, config)
        self.settings = settings  # Used for setting settings
        self.settings_path = settings_path
        self.config = config
        self.bottom_bar = None
        self.signal: ScanSignals = ScanSignals()
        self.search_signals: SearchSignals = SearchSignals()
        self.current_task = None
        self.cancel_event = threading.Event()

        self.zaber_position_timer = QTimer(self)
        self.zaber_position_timer.timeout.connect(self.emit_zaber_position)
        self.zaber_position_timer.start(1000)

    def set_settings(self, settings: Settings):
        self.settings = settings
        self.spectrometer.update_settings(settings)

    def set_config(self, config: Config):
        self.config = config
        self.spectrometer.update_config(config)
        self.signal.config_changed.emit()

    def emit_zaber_position(self):
        try:
            pos = self.spectrometer.zaber_controller.get_pos()
            self.signal.zaber_position.emit(pos)
        except Exception:
            self.signal.zaber_position.emit(-1)

    def run_scan(
        self, start_freq=None, stop_freq=11200.0, step_size=0.5, start_pos=None
    ):
        self.zaber_position_timer.stop()
        self.signal.progress.emit(-1, "Starting scan...")
        self.signal.scanning.emit(True, ScanType.FREQUENCY)
        self.current_task = asyncio.create_task(
            self._run_scan_async(start_freq, stop_freq, step_size, start_pos)
        )

    async def _run_scan_async(self, start_freq, stop_freq, step_size, start_pos=None):
        # TODO: Actually support proper progress
        try:
            await asyncio.to_thread(
                self.spectrometer.scan_frequency,
                self.signal,
                self.cancel_event,
                start_freq,
                stop_freq,
                step_size,
                start_pos,
            )
            if self.cancel_event.is_set():
                self.signal.progress.emit(1, "Scan cancelled")
            else:
                self.signal.progress.emit(1, "Scan completed")
        except Exception as e:
            self.signal.progress.emit(1, "Scan failed")
            print(f"Scan Failed: {e}")
            traceback.print_exc()
        finally:
            self.signal.scanning.emit(False, ScanType.NONE)
            self.finish_run()

    def run_search(self, cavity_type, freq=9000, step_size=0.5):
        self.zaber_position_timer.stop()
        self.signal.progress.emit(0, "Starting search...")
        self.signal.scanning.emit(True, ScanType.CAVITY)
        self.current_task = asyncio.create_task(
            self._run_search_async(cavity_type, freq, step_size)
        )

    async def _run_search_async(self, cavity_type, freq, step_size):
        try:
            await asyncio.to_thread(
                self.spectrometer.cavity_search, self.search_signals, cavity_type, freq, step_size
            )
            if self.cancel_event.is_set():
                self.signal.progress.emit(1, "Search cancelled")
            else:
                self.signal.progress.emit(1, "Search completed")
        except Exception as e:
            self.signal.progress.emit(1, "Search failed")
            print(f"Search Failed: {e}")
            traceback.print_exc()
        finally:
            self.signal.scanning.emit(False, ScanType.NONE)
            self.finish_run()

    def cancel_operation(self):
        if self.current_task:
            self.signal.progress.emit(1, "Canceling....")
            self.cancel_event.set()

    def finish_run(self):
        self.current_task = None
        self.cancel_event.clear()
        self.zaber_position_timer.start()

    async def refresh_device(self, device_id):
        success = await self.init_device_async(device_id)
        return success

    async def init_device_async(self, device_name):
        self.signal.device_status_changed.emit(device_name, DeviceStatus.CONNECTING)
        success = await asyncio.to_thread(
            self.spectrometer.init_device, f"{device_name}_controller", self.config
        )
        status = DeviceStatus.ONLINE if success else DeviceStatus.OFFLINE
        self.signal.device_status_changed.emit(device_name, status)
        return success

    async def initialize_all_devices(self):
        devices = [
            "zaber",
            "oscilloscope",
            "valon",
            "switch",
            "delay_generator",
            "awg",
        ]

        await asyncio.gather(
            *[self.init_device_async(device_name) for device_name in devices]
        )
