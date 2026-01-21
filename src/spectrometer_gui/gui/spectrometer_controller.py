import asyncio
from enum import Enum
from PySide6.QtCore import Signal, QObject

from gui.bottom_bar import BottomBarPanel

from spectrometer import Spectrometer


class DeviceStatus(Enum):
    CONNECTING = "connecting"
    ONLINE = "online"
    OFFLINE = "offline"


class SpectrometerController(QObject):
    device_status_changed = Signal(str, object)  # device_id, DeviceStatus

    def __init__(self, spectrometer: Spectrometer, bottom_bar: BottomBarPanel):
        super().__init__()
        self.spectrometer = spectrometer
        self.bottom_bar = bottom_bar
        self.current_task = None

    def run_scan(self, start_freq=None, stop_freq=11200, step_size=0.5):
        self.bottom_bar.set_status_elements(0, "Starting scan...")
        self.current_task = asyncio.create_task(
            self._run_scan_async(start_freq, stop_freq, step_size)
        )

    async def _run_scan_async(self, start_freq, stop_freq, step_size):
        # TODO: Actually support proper progress
        try:
            await asyncio.to_thread(
                self.spectrometer.scan_frequency, start_freq, stop_freq, step_size
            )
            self.bottom_bar.set_status_elements(1, "Scan completed")
        except asyncio.CancelledError:
            self.bottom_bar.set_status_elements(1, "Scan cancelled")
        finally:
            self.current_task = None

    def run_search(self, freq=9000, step_size=0.5):
        self.bottom_bar.set_status_elements(0, "Starting search...")
        self.current_task = asyncio.create_task(self._run_search_async(freq, step_size))

    async def _run_search_async(self, freq, step_size):
        # TODO:  Actually support proper progress
        try:
            await asyncio.to_thread(self.spectrometer.cavity_search, freq, step_size)
            self.bottom_bar.set_status_elements(1, "Search completed")
        except asyncio.CancelledError:
            self.bottom_bar.set_status_elements(1, "Search cancelled")
        finally:
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
            self.spectrometer.init_device, f"{device_name}_controller"
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
