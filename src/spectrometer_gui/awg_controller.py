from enum import Enum

import pyvisa as visa


class RunMode(Enum):
    Triggered = "TRIGgered"
    Continous = "CONTinuous"


class AWGController:
    def __init__(self):
        self.__visa_address = "UNKNOWN-REPLACE"
        self.__rm = visa.ResourceManager()
        self.__awg = self.__rm.open_resource(self.__visa_address)
        print("AWG connected successfully.")

    def __write_cmd(self, command):
        return self.__awg.write(command)

    def run(self):
        self.__write_cmd("AWGControl:RUN")

    def stop(self):
        self.__write_cmd("AWGControl:STOP")

    def get_status(self):
        return self.__write_cmd("AWGCONTROL:RSTATE?")

    def get_run_mode(self):
        return self.__write_cmd("AWGControl:RMODe?")

    def set_run_mode(self, mode):
        self.__write_cmd(f"AWGControl:RMODe {mode}")

    def enable_channel_output(self, channel: int):
        self.__write_cmd(f"OUTPUT{channel}:STATE ON")

    def disable_channel_output(self, channel: int):
        self.__write_cmd(f"OUTPUT{channel}:STATE OFF")

    def get_channel_output_state(self, channel: int):
        self.__write_cmd(f"OUTPUT{channel}:STATE?")

    def __reset(self):
        self.__write_cmd("*RST")
