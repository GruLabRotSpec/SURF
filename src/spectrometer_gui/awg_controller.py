from enum import Enum

import pyvisa as visa

from config import Config


class RunMode(Enum):
    Triggered = "TRIGgered"
    Continous = "CONTinuous"


class AWGController:
    def __init__(self):
        self.initialized = False

    def initialize(self, config: Config):
        self._visa_address = "GPIB1::2::INSTR"
        self._rm = visa.ResourceManager()
        self._awg = self._rm.open_resource(self._visa_address)
        self.update_config(config)
        print("AWG connected successfully.")

    def is_initialized(self) -> bool:
        return self.initialized

    def update_config(self, config: Config):
        awg_config = config.awg_controller

        if awg_config.awg_run_mode is not None:
            self.set_run_mode(awg_config.awg_run_mode)

        self.set_channel_output(1, awg_config.awg_ch_1_output)
        self.set_channel_output(2, awg_config.awg_ch_2_output)

        self.awg_freq = awg_config.awg_freq

    def _write_cmd(self, command):
        return self._awg.write(command)

    def run(self):
        self._write_cmd("AWGControl:RUN")

    def stop(self):
        self._write_cmd("AWGControl:STOP")

    def get_status(self):
        return self._write_cmd("AWGCONTROL:RSTATe?")

    def get_run_mode(self):
        return self._write_cmd("AWGControl:RMODe?")

    def set_run_mode(self, mode):
        self._write_cmd(f"AWGControl:RMODe {mode}")

    def set_channel_output(self, channel: int, state: bool):
        if state:
            self._write_cmd(f"OUTPUT{channel}:STATE ON")
        else:
            self._write_cmd(f"OUTPUT{channel}:STATE OFF")

    def get_channel_output_state(self, channel: int):
        self._write_cmd(f"OUTPUT{channel}:STATE?")

    def reset(self):
        self._write_cmd("*RST")
