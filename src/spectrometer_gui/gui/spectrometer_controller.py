import asyncio

from gui.bottom_bar import BottomBarPanel

from spectrometer import Spectrometer
from delay_generator_controller import DelayGeneratorController
from zaber_controller import ZaberController
from oscilloscope_controller import OscilloscopeController
from valon_controller import ValonController
from switch_controller import SwitchController
from awg_controller import AWGController


class SpectrometerController:
    def __init__(self, spectrometer: Spectrometer, bottom_bar: BottomBarPanel):
        self.spectrometer = spectrometer
        self.bottom_bar = bottom_bar
        self.current_task = None

    def run_scan(self, start_freq=None, stop_freq=11200, step_size=0.5):
        self.bottom_bar.set_status_elements(0, "Starting scan...")

        self.current_task = asyncio.create_task(
            self._run_scan_async(start_freq, stop_freq, step_size)
        )

    async def _run_scan_async(self, start_freq, stop_freq, step_size):
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

        # Create and manage async task
        self.current_task = asyncio.create_task(self._run_search_async(freq, step_size))

    async def _run_search_async(self, freq, step_size):
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

    async def init_device_async(self, device_id):
        """Public async wrapper for device initialization"""
        device_mapping = {
            "zaber": (
                "zaber_controller",
                ZaberController,
                [self.spectrometer.__zaber_speed],
            ),
            "oscilloscope": ("oscilloscope_controller", OscilloscopeController, []),
            "valon": ("valon_controller", ValonController, ["COM3"]),
            "switch": ("switch_controller", SwitchController, []),
            "delay_generator": (
                "delay_generator_controller",
                DelayGeneratorController,
                [],
            ),
            "awg": ("awg_controller", AWGController, []),
        }

        attr_name, controller_class, args = device_mapping[device_id]

        success = self.spectrometer.init_device(attr_name, controller_class, args)

        flag_name = f"{device_id}_initialized"
        setattr(self.spectrometer, flag_name, success)

        return success

    async def initialize_spectrometer(self):
        """Initialize spectrometer using moved initialize function"""
        # Initialize each device and track status
        device_configs = [
            ("delay_generator", DelayGeneratorController, []),
            ("zaber", ZaberController, [self.spectrometer.__zaber_speed]),
            ("oscilloscope", OscilloscopeController, []),
            ("valon", ValonController, ["COM3"]),
            ("switch", SwitchController, []),
            ("awg", AWGController, []),
        ]

        for device_id, controller_class, args in device_configs:
            attr_name = f"{device_id}_controller"
            success = self.spectrometer.init_device(attr_name, controller_class, args)
            flag_name = f"{device_id}_initialized"
            setattr(self.spectrometer, flag_name, success)
