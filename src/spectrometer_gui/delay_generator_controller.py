import pyvisa as visa

from config import Config


class DelayGeneratorController:
    def __init__(self):
        self.initialized = False

    def initialize(self, config: Config):
        self._visa_address = "GPIB0::9::INSTR"
        self._rm = visa.ResourceManager()
        self._delay_generator = self._rm.open_resource(self._visa_address)
        self._frequency = 0
        self._delays = {"T0": "1", "A": "2", "B": "3", "C": "5", "D": "6"}
        self.stop_pulse()

        # Turn on external trigger
        self._write_cmd("TM 1; TL 1")

        self.update_config(config)

        self.initialized = True

    def is_initialized(self) -> bool:
        return self.initialized  # TODO: Verify the resource is still open

    def update_config(self, config: Config):
        self.trigger_rate = config.delay_generator_controller.trigger_rate

    # Writes a command to the delay generator and returns the output
    def _write_cmd(self, command):
        return self._delay_generator.write(command)

    def set_delays(self, new_delays):
        self._delays = new_delays

    def get_delays(self):
        return self._delays

    def set_frequency(self, freq):
        self._frequency = float(freq)
        print("Activating internal trigger at ", self._frequency)
        return self._frequency

    def start_trig(self):
        write_str = "TR 0, " + str(self._frequency)
        self._write_cmd(write_str)
        write_str = "TM 0"
        self._write_cmd(write_str)
        print("Activating internal trigger at ", str(self._frequency))

    def stop_trig(self):
        write_string = "TM 1; TL 1"
        self._write_cmd(write_string)

    def start_pulse(self):
        write_string = "DT 3,2,100E-9"
        self._write_cmd(write_string)

    def stop_pulse(self):
        write_string = "DT 3,2,0"
        self._write_cmd(write_string)

    def set_trig(self, freq):
        write_string = "TM 0; TR 0, " + str(freq)
        self._write_cmd(write_string)
        print("Activating internal trigger at ", str(freq))
