import asyncio
from unittest.mock import Mock

from config import Config
from gui.spectrometer_controller import SpectrometerController
from settings import AnalysisSettings, LoggingConfig, OutputConfig, ScopePreset, Settings


class DummySpectrometer:
    def __init__(self):
        self.update_config = Mock()


def make_config():
    return Config(
        valon_controller={
            "rf_output": True,
            "rf_level": 0,
            "valon_port": "COM1",
            "synth_power": True,
            "ref_source": "Internal",
            "ref_freq": 10.0,
            "freq": 8000.0,
        },
        zaber_controller={
            "zaber_scanning_speed": 0.1,
            "zaber_moving_speed": 0.2,
            "zaber_step_size": 0.3,
            "zaber_port": "COM2",
        },
        awg_controller={
            "awg_status": True,
            "awg_freq": 10,
            "awg_run_mode": "Continuous",
            "awg_ch_1_output": True,
            "awg_ch_2_output": False,
        },
        oscilloscope_controller={
            "channel": "CH1",
            "acq_rate": 100,
            "sample_rate": 500,
            "math_averages": 2,
            "visa_address": "TCPIP::scope::INSTR",
            "math3": {
                "window": "Hanning",
                "resolution": 100.0,
                "gate_position": 1.0,
                "scale": 1.0,
            },
            "math4": {
                "window": "Hanning",
                "resolution": 200.0,
                "gate_position": 2.0,
                "scale": 2.0,
            },
            "math3_cont": {
                "window": "Hanning",
                "resolution": 300.0,
                "gate_position": 3.0,
                "scale": 3.0,
            },
        },
        delay_generator_controller={
            "trigger_rate": 100.0,
            "trigger_state": "INT",
        },
    )


def test_apply_config_async_updates_spectrometer_in_thread():
    settings = Settings(
        output=OutputConfig(location="/tmp", filename="scan"),
        logging=LoggingConfig(enabled=True, location="/tmp/logs"),
        scope_preset=ScopePreset(root_path="/tmp/presets", presets={}),
        analysis=AnalysisSettings(),
    )
    controller = SpectrometerController(settings, make_config())
    controller.spectrometer = DummySpectrometer()

    async def run_test():
        config = make_config()
        await controller.apply_config_async(config)

    asyncio.run(run_test())

    controller.spectrometer.update_config.assert_called_once()
    assert controller.config == controller.spectrometer.update_config.call_args.args[0]
