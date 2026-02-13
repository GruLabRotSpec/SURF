import time
import serial

from config import Config


class ValonController:
    def __init__(self):
        self._delay = 0.1

    def initialize(self, config: Config):
        con = serial.Serial(
            port=config.valon_controller.valon_port, baudrate=9600, timeout=3
        )

        con.setDTR(False)  # type: ignore
        con.reset_input_buffer()
        con.setDTR(True)  # type: ignore

        con.write(b"ID?\r")
        response_bytes = con.read(1024)
        print(response_bytes)

        time.sleep(0.5)

        self._connection = con

    def is_initialized(self) -> bool:
        return self._connection.is_open if hasattr(self, "_connection") else False

    # Write Valon cmds, either writing or querying based on presence of \r
    def write_cmd(self, cmd):
        # Format command with line termination \r, encode (utf-8 I think), send to Valon
        format_cmd = f"{cmd}"
        format_cmd += "\r"
        self._connection.reset_input_buffer()
        print(format_cmd)
        self._connection.write(format_cmd.encode())
        time.sleep(self._delay)
        response_bytes = self._connection.read(1024)
        response = response_bytes.decode().strip()
        print(response)
        return response

    def set_settings(self, rf_level):
        print("Establishing Valon Settings: ")
        self.write_cmd("MODe CW")
        self.write_cmd("PDN 1")
        self.write_cmd("REFS 0")
        self.write_cmd("PoWeR?")
        self.write_cmd(f"PoWeR{rf_level}")

        self.write_cmd("OEN 1")

    def set_step_size_sweep(self, step_size):  ## for Chirp pulse sweep not Cavity
        self.write_cmd(f"STEP {step_size}M")

    def start_sweep(self, start_freq):
        self.write_cmd(f"STARt {start_freq}M")

    def stop_sweep(self, stop_freq):
        self.write_cmd(f"STOP {stop_freq}M")

    def set_sweep_rate(self, sweep_rate):
        self.write_cmd(f"RATE {sweep_rate}")  # In ms

    def sweep_mode(self, start, stop, step, rate):
        self.start_sweep(start)
        self.stop_sweep(stop)
        self.set_step_size_sweep(step)
        self.set_sweep_rate(rate)
        self.write_cmd("MODe SWEep")

    ## Continuous wave settings
    def step_up(self):
        self.write_cmd("FrequencyINCRement")
        valon_freq = self.write_cmd("Frequency")
        print(valon_freq)

    def step_down(self):
        self.write_cmd("FrequencyDECRement")
        valon_freq = self.write_cmd("Frequency")
        print(valon_freq)

    def frequency_step_cw(self, step_size):
        self.write_cmd(f"FrequencyStep {step_size}M")
        self.write_cmd("Frequency")
