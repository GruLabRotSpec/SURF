import asyncio

from gui.bottom_bar import BottomBarPanel

from spectrometer import Spectrometer


class SpectrometerController:
    def __init__(self, spectrometer: Spectrometer, bottom_bar: BottomBarPanel):
        self.spectrometer = spectrometer
        self.bottom_bar = bottom_bar

    async def run_scan(self, start_freq=None, stop_freq=11200, step_size=0.5):
        await self.spectrometer.scan_frequency(start_freq, stop_freq, step_size)

    async def run_search(self, freq=9000, step_size=0.5):
        await self.spectrometer.cavity_search(freq, step_size)
