import serial
import time

from v_serial_port import VSerialPort


class ValonController:
    def __init__(self, port = "COM3"):
        self.__delay = 0.1
        self.__port = port
        self.__connection = VSerialPort.VSerialPort(self.__port)


# Write Valon cmds, either writing or querying based on presence of \r
def write_cmd(cmd):
    # Format command with line termination \r, encode (utf-8 I think), send to Valon
    format_cmd = f"{cmd}"
    format_cmd += "\r"
    self.__connection.reset_input_buffer()
    print(format_cmd)
    self.__connection.write(format_cmd.encode())
    time.sleep(delay)
    response_bytes = self.__connection.read(1024)
    response = response_bytes.decode().strip()
    print(response)
    return response


def set_settings(rf_level):
    print("Establishing Valon Settings: ")
    write_cmd("MODe CW")
    write_cmd("PDN 1")
    write_cmd("REFS 0")
    write_cmd("PoWeR?")
    write_cmd(f"PoWeR{rf_level}")

    write_cmd("OEN 1")


def set_step_size_sweep(step_size):  ## for Chirp pulse sweep not Cavity
    write_cmd(f"STEP {step_size}M")


def start_sweep(start_freq):
    write_cmd(f"STARt {start_freq}M")


def stop_sweep(stop_freq):
    write_cmd(f"STOP {stop_freq}M")


def set_sweep_rate(sweep_rate):
    write_cmd(f"RATE {sweep_rate}")  # In ms


def sweep_mode(start, stop, step, rate):
    start_sweep(start)
    stop_sweep(stop)
    set_step_size_sweep(step)
    set_sweep_rate(rate)
    write_cmd("MODe SWEep")


## Continuous wave settings
def step_up():
    write_cmd("FrequencyINCRement")
    valon_freq = write_cmd("Frequency")
    print(valon_freq)


def step_down():
    write_cmd("FrequencyDECRement")
    valon_freq = write_cmd("Frequency")
    print(valon_freq)


def frequency_step_cw(step_size):
    write_cmd(f"FrequencyStep {step_size}M")
    write_cmd("Frequency")
