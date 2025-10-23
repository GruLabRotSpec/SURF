import pyvisa as visa

class DelayGeneratorController:
    def __init__(self):
        self.__visa_address = "GPIB0::9::INSTR"
        self.__rm = visa.ResourceManager()
        self.__delay_generator = self.__rm.open_resource(self.__visa_address)
        self.__frequency = 0
        self.__delays = {"T0": "1", "A": "2", "B": "3", "C": "5", "D": "6"}
        print("_______________________________________________________")
        print("SRS opened successfully... Switching to EXT Triggering.")
        print("_______________________________________________________")
        self.stop_pulse()
        # Turn on external trigger
        self.__write_cmd("TM 1; TL 1")

    # Writes a command to the delay generator and returns the output
    def __write_cmd(self, command):
        return self.__delay_generator.write(command)

    def set_delays(self, new_delays):
        self.__delays = new_delays

    def get_delays(self):
        return self.__delays

    def set_frequency(self, freq):
        self.__frequency = float(freq)
        print("Activating internal trigger at ", self.__frequency)
        return self.__frequency

    def start_trig(self):
        write_str = "TR 0, " + str(self.__frequency)
        self.__write_cmd(write_str)
        write_str = "TM 0"
        self.__write_cmd(write_str)
        print("Activating internal trigger at ", str(self.__frequency))

    def stop_trig(self):
        write_string = "TM 1; TL 1"
        self.__write_cmd(write_string)

    def start_pulse(self):
        write_string = "DT 3,2,100E-9"
        self.__write_cmd(write_string)

    def stop_pulse(self):
        write_string = "DT 3,2,0"
        self.__write_cmd(write_string)

    def set_trig(self, freq):
        write_string = "TM 0; TR 0, " + str(freq)
        self.__write_cmd(write_string)
        print("Activating internal trigger at ", str(freq))
