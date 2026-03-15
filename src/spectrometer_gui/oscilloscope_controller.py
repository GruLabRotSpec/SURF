import time
import pyvisa as visa
import numpy as np

from config import Config


class OscilloscopeController:
    # initializing scope
    def __init__(self):
        self.initialized = False

    def initialize(self, config: Config):
        rm = visa.ResourceManager()
        self.__visa_address = "TCPIP0::169.254.23.223::inst0::INSTR"
        self.__oscilloscope = rm.open_resource(
            self.__visa_address
        )  # delay after each command
        self.__oscilloscope.timeout = 10000  # ms
        self.__oscilloscope.encoding = "latin_1"
        self.__oscilloscope.write_termination = "\n"
        self.__oscilloscope.expect_termination = False
        self.__oscilloscope.chunk_size = 102400  # larger data sizes
        time.sleep(1)
        r = self.__oscilloscope.query("*opc?")  # sync
        print(r)
        self.__oscilloscope.write("*cls")

        self.update_config(config)
        self.initialized = True

    def is_initialized(self) -> bool:
        return self.initialized  # TODO: Verify the resource is still open

    def update_config(self, config: Config):
        oscill_config = config.oscilloscope_controller

        self.write_cmd(f"MATH4:SPECTral:WINdow {oscill_config.window_type}")
        self.write_cmd(f"HORizontal:MODE:SAMPLERate {oscill_config.sample_rate}e6")
        self.write_cmd(f"MATH4:SPECTral:RESBw {oscill_config.resolution}e3") # Convert to Hz
        self.write_cmd(f"MATH4:SPECTral:GATEPOS {oscill_config.gate_position}e-6")
        self.write_cmd(f"MATH4:NUMAvg {oscill_config.math_averages}")

        self.channel = oscill_config.channel
        self.gate_pos = oscill_config.gate_position

    # sends command, ensures no error after
    def write_cmd(self, command):
        self.__oscilloscope.write(command)
        errorCheck = self.__oscilloscope.write("*ESR?")

        # ESR giving command error "5": Command Error. Shows that an error occurred while the
        # instrument was parsing a command or query.
        if errorCheck != 6:
            print(f"Command status register error: {errorCheck}")

        self.__oscilloscope.write("*cls")

    # query command
    def query_cmd(self, command):
        output = self.__oscilloscope.query(f"{command}")
        return output

    # grabParam for generating waveform plot
    def grab_param(self):
        timeScale = float(self.query_cmd("wfmoutpre:xincr?"))  # horizontal spacing
        timeStart = float(self.query_cmd("wfmoutpre:xzero?"))
        verticalScale = float(self.query_cmd("wfmoutpre:ymult?"))  # volts / level
        verticalOffset = float(self.query_cmd("wfmoutpre:yzero?"))  # reference voltage
        verticalPosition = float(
            self.query_cmd("wfmoutpre:yoff?")
        )  # reference position (level)

        FreqCent = float(self.query_cmd("MATH4:SPECTral:CENTER?"))
        FreqSpan = float(self.query_cmd("MATH4:SPECTral:SPAN?"))
        Resolution = float(self.query_cmd("MATH4:SPECTral:RESBw?"))
        GatePos = float(self.query_cmd("MATH4:SPECTral:GATEPOS?"))
        GateWidth = float(self.query_cmd("MATH4:SPECTral:GATEWIDTH?"))

        return (
            timeScale,
            timeStart,
            verticalScale,
            verticalOffset,
            verticalPosition,
            FreqCent,
            FreqSpan,
            Resolution,
            GatePos,
            GateWidth,
        )

    # starts oscilloscope run
    def calib_start(self):
        # initial config
        self.write_cmd("acquire:state 0")
        self.write_cmd("header 0")
        self.write_cmd("data:encdg SRIBINARY")
        self.write_cmd("data:source CH1")  # channel
        self.write_cmd("wfmoutpre:byt_n 1")  # 1 byte per sample

        # acq config
        self.write_cmd("acquire:state 0")  # stop
        self.write_cmd("acquire:STOPAfter RUNSTop")  # cont
        self.write_cmd("acquire:state 1")

    # stops oscilloscope run
    def calib_stop(self):
        self.write_cmd("acquire:state 0")

    def clear(self):
        self.write_cmd("CLEAR ALL")  # doesn't work

    def run(self):
        self.write_cmd("acquire:state 1")  # run

    def acquire_fft_data_at_max(self):
        # math4 input param
        self.write_cmd("header 0")
        self.write_cmd("data:encdg SRPbinary")
        self.write_cmd("data:source MATH4")  # channel
        self.write_cmd("wfmoutpre:byt_nr 4")

        # io config
        self.write_cmd("header 0")
        self.write_cmd("data:encdg SRPbinary")
        self.write_cmd("data:start 1")  # first sample
        self.write_cmd("wfmoutpre:byt_nr 4")

        # acq config
        self.write_cmd("acquire:state 0")  # stop
        self.write_cmd("acquire:STOPAfter RUNSTop")  # cont acq
        self.write_cmd("curvestream?")
        self.write_cmd("acquire:state 1")  # run

        # data query
        t7 = time.perf_counter()
        bin_wave = self.__oscilloscope.query_binary_values(
            "curve?", datatype="f", container=np.array, is_big_endian=True
        )
        t8 = time.perf_counter()
        print("acquire time: ", t8 - t7)

        self.write_cmd("WFMOutpre?")

        return bin_wave

    def recall_setup(
        self,
        setup,
        folder="C:\\Documents and Settings\\Administrator\\My Documents\\Setups_for_lab",
    ):
        self.write_cmd(f'RECALL:SETUP "{folder}\\{setup}"')
        time.sleep(3)
        print("Successfully recalled setup")

    def recall_setup_cavity(self, setup="cavity_ch2000002.set"):
        self.write_cmd(f'RECALL:SETUP "{setup}"')
        time.sleep(7)

    def recall_mol_peak(self, setup="cavity000.set"):
        self.write_cmd(f'RECALL:SETUP "{setup}"')
        time.sleep(7)

    def acq_ft_curve(self, acqtime):  # this is for actually pulling the data
        self.write_cmd("header 0")
        self.write_cmd("data:encdg SRPbinary")
        self.write_cmd("data:source MATH4")  # channel
        self.write_cmd("wfmoutpre:byt_nr 4")
        recordLength = int(self.query_cmd("horizontal:recordlength?"))
        self.write_cmd("data:stop {}".format(recordLength))

        # acq configuration
        self.write_cmd("acquire:state 0")  # stop
        self.write_cmd("acquire:STOPAfter RUNSTop")  # cont acq
        self.write_cmd("curvestream?")
        self.write_cmd("acquire:state 1")  # run
        self.write_cmd(f"{self.channel}:SCAle 0.9")

        # data query
        time.sleep(acqtime)
        t7 = time.perf_counter()
        new_bin_wave = self.__oscilloscope.query_binary_values(
            "curve?", datatype="f", container=np.array, is_big_endian=True
        )
        t8 = time.perf_counter()
        print("acquire time: ", t8 - t7)

        self.write_cmd("WFMOutpre?")

        return new_bin_wave

    def set_settings(self):
        self.write_cmd("SELECT:MATH3 0")
        self.write_cmd(f'MATH4:DEFINE "SpectralMag(AVG({self.channel}))"')
        self.write_cmd("SELECT:MATH4 1")
        self.write_cmd("MATH4:NUMAvg 1000000")
        self.write_cmd("MATH4:VERTical:POSition -4")
        self.write_cmd("MATH4:SPECTral:WINdow Hanning")
        self.write_cmd("HORizontal:MODE:SAMPLERate 500E6")
        self.write_cmd("HORizontal:MODE:SCAle 5E-6")                    ##! parameters to reset each time
        self.write_cmd("MATH4:SPECTral:RESBw 100E3")                    ##
        self.write_cmd("MATH4:SPECTral:CENTER 30E6")                    ##
        self.write_cmd("MATH4:SPECTral:SPAN 20E6")                      ##
        self.write_cmd(f"MATH4:SPECTral:GATEPOS {self.gate_pos}")       ##
        self.write_cmd(                                                 ##
            "MATH4:VERTICAL:SCALE 500E-6"                   
        )  # sets math channel vertical scale
        # time.sleep(2)
        self.write_cmd(f"{self.channel}:SCAle 1")

    def set_tuning_settings(self):
        self.write_cmd("SELECT:MATH4 0")

        self.write_cmd(f'MATH3:DEFINE "SpectralMag({self.channel})"')
        self.write_cmd("SELECT:MATH3 1")
        self.write_cmd("MATH3:SPECTral:WINdow Rectangular")
        self.write_cmd("MATH3:VERTical:POSition -4")
        self.write_cmd("HORizontal:MODE:SAMPLERate 500E6")
        self.write_cmd("HORizontal:MODE:SCAle 500E-9")          ##! parameters to reset each time
        self.write_cmd("MATH3:SPECTral:RESBw 890E3")            ##
        self.write_cmd("MATH3:SPECTral:CENTER 30E6")            ##
        self.write_cmd("MATH3:SPECTral:GATEPOS 600E-9")         ##
        self.write_cmd("MATH3:VERTICAL:SCALE 5E-3")  # sets math channel vertical scale

        self.calib_start()
