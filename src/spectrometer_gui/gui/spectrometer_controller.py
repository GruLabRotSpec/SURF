import asyncio
from enum import Enum
from PySide6.QtCore import Signal, QObject

from gui.bottom_bar import BottomBarPanel

from spectrometer import Spectrometer
from config import Config


class DeviceStatus(Enum):
    CONNECTING = "connecting"
    ONLINE = "online"
    OFFLINE = "offline"


class ScanType(Enum):
    NONE = 0
    FREQUENCY = 1
    CAVITY = 2


class SpectrometerController(QObject):
    device_status_changed = Signal(str, DeviceStatus)  # device_id, DeviceStatus
    scanning = Signal(bool, ScanType)

    def __init__(self, config: Config, bottom_bar: BottomBarPanel):
        super().__init__()
        self.spectrometer = Spectrometer(config)
        self.config = config
        self.bottom_bar = bottom_bar
        self.current_task = None

    def set_config(self, config: Config):
        self.config = config
        self.spectrometer.update_config(config)

    def run_scan(self, start_freq=None, stop_freq=11200.0, step_size=0.5):
        self.bottom_bar.set_status_elements(-1, "Starting scan...")
        self.scanning.emit(True, ScanType.FREQUENCY)
        self.current_task = asyncio.create_task(
            self._run_scan_async(start_freq, stop_freq, step_size)
        )

    def scan_callback(self, progress: float):
        print(f"Progress Updated: {progress}")
        self.bottom_bar.set_status_elements(progress, "Scanning...")

    async def _run_scan_async(self, loop, start_freq, stop_freq, step_size):
        # TODO: Actually support proper progress
        loop = asyncio.get_running_loop()
        try:
            await asyncio.to_thread(
                self.spectrometer.scan_frequency, loop, self.scan_callback, start_freq, stop_freq, step_size
            )
            self.bottom_bar.set_status_elements(1, "Scan completed")
        except asyncio.CancelledError:
            self.bottom_bar.set_status_elements(1, "Scan cancelled")
        except Exception as e:
            self.bottom_bar.set_status_elements(1, "Scan failed")
            print(f"Scan Failed: {e}")
        finally:
            self.scanning.emit(False, ScanType.NONE)
            self.current_task = None

    def run_search(self, freq=9000, step_size=0.5):
        self.bottom_bar.set_status_elements(0, "Starting search...")
        self.scanning.emit(True, ScanType.CAVITY)
        self.current_task = asyncio.create_task(self._run_search_async(freq, step_size))

    async def _run_search_async(self, freq, step_size):
        try:
            await asyncio.to_thread(self.spectrometer.cavity_search, freq, step_size)
            self.bottom_bar.set_status_elements(1, "Search completed")
        except asyncio.CancelledError:
            self.bottom_bar.set_status_elements(1, "Search cancelled")
        except Exception as e:
            self.bottom_bar.set_status_elements(1, "Search failed")
            print(f"Search Failed: {e}")
        finally:
            self.scanning.emit(False, ScanType.NONE)
            self.current_task = None

    def cancel_operation(self):
        if self.current_task:
            self.current_task.cancel()

    async def refresh_device(self, device_id):
        success = await self.init_device_async(device_id)
        return success

    async def init_device_async(self, device_name):
        self.device_status_changed.emit(device_name, DeviceStatus.CONNECTING)
        success = await asyncio.to_thread(
            self.spectrometer.init_device, f"{device_name}_controller", self.config
        )
        status = DeviceStatus.ONLINE if success else DeviceStatus.OFFLINE
        self.device_status_changed.emit(device_name, status)
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
