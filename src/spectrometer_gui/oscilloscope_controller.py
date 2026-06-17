import time
import pyvisa as visa
import numpy as np

from config import Config


class OscilloscopeController:
    def __init__(self):
        self.initialized = False

    def initialize(self, config: Config):
        rm = visa.ResourceManager()
        self._visa_address = config.oscilloscope_controller.visa_address
        self._oscilloscope = rm.open_resource(
            self._visa_address
        )  # delay after each command
        self._oscilloscope.timeout = 10000  # ms
        self._oscilloscope.encoding = "latin_1"
        self._oscilloscope.write_termination = "\n"
        self._oscilloscope.expect_termination = False
        self._oscilloscope.chunk_size = 102400  # larger data sizes

        time.sleep(1)

        r = self._oscilloscope.query("*opc?")  # sync
        print(f"Scope Query: {r}")
        self._oscilloscope.write("*cls")

        self.update_config(config)
        self.initialized = True

    def is_initialized(self) -> bool:
        return self.initialized  # TODO: Verify the resource is still open

    def update_config(self, config: Config):
        oscill_config = config.oscilloscope_controller

        self.write_cmd(f"HORizontal:MODE:SAMPLERate {oscill_config.sample_rate}e6")

        # Math 3
        self.write_cmd(f"MATH3:SPECTral:WINdow {oscill_config.math3.window}")
        self.write_cmd(f"MATH3:SPECTral:RESBw {oscill_config.math3.resolution}e3")
        self.write_cmd(f"MATH3:SPECTral:GATEPOS {oscill_config.math3.gate_position}e-6")
        self.write_cmd(f"MATH3:NUMAvg {oscill_config.math_averages}")

        # Math 4
        self.write_cmd(f"MATH4:SPECTral:WINdow {oscill_config.math4.window}")
        self.write_cmd(f"MATH4:SPECTral:RESBw {oscill_config.math4.resolution}e3")
        self.write_cmd(f"MATH4:SPECTral:GATEPOS {oscill_config.math4.gate_position}e-6")
        self.write_cmd(f"MATH4:NUMAvg {oscill_config.math_averages}")

        self.channel = oscill_config.channel
        self.acq_rate = oscill_config.acq_rate
        self.config = config

    def recall_setup(
        self,
        setup,
        folder="C:\\Documents and Settings\\Administrator\\My Documents\\Setups_for_lab",
    ):
        self.write_cmd(f'RECALL:SETUP "{folder}\\{setup}"')
        time.sleep(3)
        print("Successfully recalled setup")

    def write_cmd(self, command):
        self._oscilloscope.write(command)
        errorCheck = self._oscilloscope.write("*ESR?")

        # ESR giving command error "5": Command Error. Shows that an error occurred while the
        # instrument was parsing a command or query.
        if errorCheck != 6:
            print(f"Command status register error: {errorCheck}")

        self._oscilloscope.write("*cls")

        # Give the scope a small amount of time to update
        time.sleep(0.1)

    def query_cmd(self, command):
        output = self._oscilloscope.query(f"{command}")
        return output

    def grab_fft_params(self):
        time_scale = float(self.query_cmd("wfmoutpre:xincr?"))
        time_start = float(self.query_cmd("wfmoutpre:xzero?"))
        freq_cent = float(self.query_cmd("MATH4:SPECTral:CENTER?"))
        freq_span = float(self.query_cmd("MATH4:SPECTral:SPAN?"))
        return time_scale, time_start, freq_cent, freq_span

    def start_acq(self):
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

    def stop_acq(self):
        self.write_cmd("acquire:state 0")

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
        bin_wave = self._oscilloscope.query_binary_values(
            "curve?", datatype="f", container=np.array, is_big_endian=True
        )
        t8 = time.perf_counter()
        print("fft acquire time: ", t8 - t7)

        self.write_cmd("WFMOutpre?")

        return bin_wave

    def acq_ft_curve(self, acqtime):  # this is for actually pulling the data
        self.write_cmd("header 0")
        self.write_cmd("data:encdg SRPbinary")
        self.write_cmd("data:source MATH4")  # channel
        self.write_cmd("wfmoutpre:byt_nr 4")
        recordLength = int(self.query_cmd("horizontal:recordlength?"))
        self.write_cmd(f"data:stop {recordLength}")

        # acq configuration
        self.write_cmd("acquire:state 0")  # stop
        self.write_cmd("acquire:STOPAfter RUNSTop")  # cont acq
        self.write_cmd("curvestream?")
        self.write_cmd("acquire:state 1")  # run
        self.write_cmd(f"{self.channel}:SCAle 0.9")

        # data query
        time.sleep(acqtime)
        t7 = time.perf_counter()
        new_bin_wave = self._oscilloscope.query_binary_values(
            "curve?", datatype="f", container=np.array, is_big_endian=True
        )
        t8 = time.perf_counter()
        print("ft curve acquire time: ", t8 - t7)

        self.write_cmd("WFMOutpre?")

        self.stop_acq()

        return new_bin_wave

    def set_math3(self):
        oscill_config = self.config.oscilloscope_controller
        self.write_cmd("SELECT:MATH4 0")
        self.write_cmd(f'MATH3:DEFINE "SpectralMag({self.channel})"')
        self.write_cmd("SELECT:MATH3 1")
        self.write_cmd('cursor:source MATH3')
        self.write_cmd('cursor:VBARs:Position1 29.99E6')
        self.write_cmd('cursor:VBARs:Position2 30.01E6')
        self.write_cmd('MEASUREment:MEAS1:SOURCE MATH3')
        self.write_cmd('measurement:meas1:type max')
        self.write_cmd('measurement:gating cursor')
        self.write_cmd('measurement:meas1:state 1')
        self.write_cmd(f"MATH3:SPECTral:WINdow {oscill_config.math3.window}")
        self.write_cmd(f"MATH3:SPECTral:RESBw {oscill_config.math3.resolution}e3")
        self.write_cmd("MATH3:SPECTral:CENTER 30E6")
        self.write_cmd(f"MATH3:SPECTral:GATEPOS {oscill_config.math3.gate_position}e-6")
        self.write_cmd(f"MATH3:NUMAvg {oscill_config.math_averages}")
        self.write_cmd("MATH3:VERTICAL:SCALE 5E-3")

        self.start_acq()

    def set_math4(self):
        oscill_config = self.config.oscilloscope_controller
        self.write_cmd("SELECT:MATH3 0")
        self.write_cmd(f'MATH4:DEFINE "SpectralMag(AVG({self.channel}))"')
        self.write_cmd("SELECT:MATH4 1")

        self.write_cmd(f"MATH4:SPECTral:WINdow {oscill_config.math4.window}")
        self.write_cmd(f"MATH4:SPECTral:RESBw {oscill_config.math4.resolution}e3")
        self.write_cmd("MATH4:SPECTral:CENTER 30E6")
        self.write_cmd("MATH4:SPECTral:SPAN 20E6")
        self.write_cmd(f"MATH4:SPECTral:GATEPOS {oscill_config.math4.gate_position}e-6")
        self.write_cmd(f"MATH4:NUMAvg {oscill_config.math_averages}")
        self.write_cmd("MATH4:VERTICAL:SCALE 500E-6")
        self.write_cmd(f"{self.channel}:SCAle 1")
