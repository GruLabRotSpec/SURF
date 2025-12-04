import serial
import time

from v_serial_port import VSerialPort


class ValonController:
    def __init__(self, port = "COM3"):
        self.__delay = 0.1
        self.__port = port
        self.__connection = VSerialPort(self.__port)


    # Write Valon cmds, either writing or querying based on presence of \r
    def write_cmd(self, cmd):
        # Format command with line termination \r, encode (utf-8 I think), send to Valon
        format_cmd = f"{cmd}"
        format_cmd += "\r"
        self.__connection.reset_input_buffer()
        print(format_cmd)
        self.__connection.write(format_cmd.encode())
        time.sleep(self.__delay)
        response_bytes = self.__connection.read(1024)
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
