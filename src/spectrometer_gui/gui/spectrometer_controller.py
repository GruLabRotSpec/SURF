import asyncio
import traceback
import threading
from enum import Enum

from config import Config
from gui.bottom_bar import BottomBarPanel
from PySide6.QtCore import QObject, QTimer, Signal
from settings import Settings
from spectrometer import GraphState, ScanType, Spectrometer


class DeviceStatus(Enum):
    CONNECTING = "connecting"
    ONLINE = "online"
    OFFLINE = "offline"


class ScanSignals(QObject):
    device_status_changed = Signal(str, DeviceStatus)  # device_id, DeviceStatus
    progress = Signal(float, str)
    scanning = Signal(bool, ScanType)
    update_graph = Signal(GraphState)
    zaber_position = Signal(float)  # position in mm, or -1 on error
    config_changed = Signal()


class SpectrometerController(QObject):
    def __init__(self, settings: Settings, config: Config):
        super().__init__()
        self.spectrometer = Spectrometer(settings, config)
        self.settings = settings  # Used for setting settings
        self.config = config
        self.bottom_bar = None
        self.signal: ScanSignals = ScanSignals()
        self.current_task = None
        self.cancel_event = threading.Event()

        self.zaber_position_timer = QTimer(self)
        self.zaber_position_timer.timeout.connect(self.emit_zaber_position)
        self.zaber_position_timer.start(1000)

    def set_bottom_bar(self, bottom_bar: BottomBarPanel):
        self.bottom_bar = bottom_bar

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
        self.bottom_bar.set_status_elements(-1, "Starting scan...")
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
                self.bottom_bar.set_status_elements(1, "Scan cancelled")
            else:
                self.bottom_bar.set_status_elements(1, "Scan completed")
        except Exception as e:
            self.bottom_bar.set_status_elements(1, "Scan failed")
            print(f"Scan Failed: {e}")
            traceback.print_exc()
        finally:
            self.signal.scanning.emit(False, ScanType.NONE)
            self.finish_run()

    def run_search(self, freq=9000, step_size=0.5):
        self.zaber_position_timer.stop()
        self.bottom_bar.set_status_elements(0, "Starting search...")
        self.signal.scanning.emit(True, ScanType.CAVITY)
        self.current_task = asyncio.create_task(self._run_search_async(freq, step_size))

    async def _run_search_async(self, freq, step_size):
        try:
            await asyncio.to_thread(self.spectrometer.cavity_search, freq, step_size)
            if self.cancel_event.is_set():
                self.bottom_bar.set_status_elements(1, "Search cancelled")
            else:
                self.bottom_bar.set_status_elements(1, "Search completed")
        except Exception as e:
            self.bottom_bar.set_status_elements(1, "Search failed")
            print(f"Search Failed: {e}")
            traceback.print_exc()
        finally:
            self.signal.scanning.emit(False, ScanType.NONE)
            self.finish_run()

    def cancel_operation(self):
        if self.current_task:
            self.bottom_bar.set_status_elements(1, "Canceling....")
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

        for device_name in devices:
            await self.init_device_async(device_name)
