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

        #defaults

        self.math4_resolution = 100
        self.math4_apodization = 'Hanning'
        self.math4_acq_delay = '22'
        self.math4_hor_scale = '5E-6'
        self.math4__vert_scale = '100E-6'
        self.math4_num_averages = '1000000'
        self.math4_sample_rate = '500'

        self.math3_resolution = 334
        self.math3_apodization = 'Rectangular'
        self.math3_acq_delay = '2.5'
        self.math3_hor_scale = '500E-9'
        self.math3__vert_scale = '100E-6'
        self.math3_num_averages = '2'
        self.math3_sample_rate = '500'
        
        self.acq_num = '100'
        r = self._oscilloscope.query("*opc?")  # sync
        print(f"Scope Query: {r}")
        self._oscilloscope.write("*cls")

        self.update_config(config)
        self.initialized = True

    def is_initialized(self) -> bool:
        return self.initialized  # TODO: Verify the resource is still open

    def update_config(self, config: Config):    #need to update this to match the others so config updates
        oscill_config = config.oscilloscope_controller

        self.channel = oscill_config.channel
        self.acq_num = oscill_config.acq_rate
        self.math4_acq_delay = oscill_config.math4.gate_position
        self.math4_resolution = oscill_config.math4.resolution
        self.math4_apodization = oscill_config.math4.window
        self.math4_sample_rate = oscill_config.sample_rate
        self.math4_num_averages = oscill_config.math_averages

        self.math3_apodization = oscill_config.math3.window
        self.math3_resolution  = oscill_config.math3.resolution
        self.math3_acq_delay   = oscill_config.math3.gate_position

        self.math3_apodization = oscill_config.math3_cont.window
        self.math3_resolution  = oscill_config.math3_cont.resolution
        self.math3_acq_delay   = oscill_config.math3_cont.gate_position
        self.math3_vert_scale = oscill_config.math3_cont.scale

        self.config = config
        self.set_math4()
        self.set_math3()
        self.set_math3_cont()
        # Math 3
        # self._update_math3()
        # self._update_math3_cont()

        # Math 4
        # self._update_math4()

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
        
        self.write_cmd("SELECT:MATH4 0")
        self.write_cmd(f'MATH3:DEFINE "SpectralMag({self.channel})"')
        self.write_cmd("SELECT:MATH3 1")
        self.write_cmd(f"MATH3:SPECTral:WINdow {self.math3_apodization}")
        self.write_cmd(f'HORizontal:MODE:SCAle {self.math3_hor_scale}E-9')
        self.write_cmd(f"MATH3:SPECTral:RESBw {self.math3_resolution}e3")
        self.write_cmd("MATH3:SPECTral:CENTER 30E6")
        self.write_cmd("MATH4:SPECTral:SPAN 40E6")
        self.write_cmd("cursor:source MATH3")
        self.write_cmd("cursor:VBARs:Position1 29.95E6")
        self.write_cmd("cursor:VBARs:Position2 30.05E6")
        self.write_cmd("MEASUREment:MEAS1:SOURCE MATH3")
        self.write_cmd("measurement:meas1:type max")
        self.write_cmd("measurement:gating cursor")
        self.write_cmd("measurement:meas1:state 1")

        self.write_cmd(f"MATH3:SPECTral:GATEPOS {self.math3_acq_delay}e-6")
        self.write_cmd(f"MATH3:NUMAvg {self.math3_num_averages}")
        self.write_cmd(f"MATH3:VERTICAL:SCALE {self.math3__vert_scale}E-3")

        self.start_acq()

    def set_math3_cont(self):
        oscill_config = self.config.oscilloscope_controller
        self.write_cmd("SELECT:MATH4 0")
        self.write_cmd(f'MATH3:DEFINE "SpectralMag({self.channel})"')
        self.write_cmd("SELECT:MATH3 1")

        self.write_cmd(f"MATH3:SPECTral:WINdow {oscill_config.math3_cont.window}")
        self.write_cmd(f"MATH3:SPECTral:RESBw {oscill_config.math3_cont.resolution}e3")
        self.write_cmd("MATH3:SPECTral:CENTER 30E6")
        self.write_cmd(
            f"MATH3:SPECTral:GATEPOS {oscill_config.math3_cont.gate_position}e-6"
        )
        self.write_cmd(f"MATH3:NUMAvg {oscill_config.math_averages}")
        self.write_cmd("MATH3:VERTICAL:SCALE 5E-3")

    def set_math4(self):
        self.write_cmd("SELECT:MATH3 0")
        self.write_cmd(f'MATH4:DEFINE "SpectralMag(AVG({self.channel}))"')
        self.write_cmd("SELECT:MATH4 1")

        self.write_cmd(f"MATH4:SPECTral:WINdow {self.math4_apodization}")
        self.write_cmd(f'HORizontal:MODE:SCAle {self.math4_hor_scale}')
        self.write_cmd(f"MATH4:SPECTral:RESBw {self.math4_resolution}e3")
        self.write_cmd("MATH4:SPECTral:CENTER 30E6")
        self.write_cmd("MATH4:SPECTral:SPAN 20E6")
        self.write_cmd(f"MATH4:SPECTral:GATEPOS {self.math4_acq_delay}e-6")
        self.write_cmd(f"MATH4:NUMAvg {self.math4_num_averages}")
        self.write_cmd(f"MATH4:VERTICAL:SCALE {self.math4__vert_scale}E-6")
        self.write_cmd(f"{self.channel}:SCAle 1")

        self.start_acq()

    def _update_math3(self):
        oscill_config = self.config.oscilloscope_controller
        self.write_cmd(f"MATH3:SPECTral:WINdow {oscill_config.math3.window}")
        self.write_cmd(f"MATH3:SPECTral:RESBw {oscill_config.math3.resolution}e3")
        self.write_cmd(f"MATH3:SPECTral:GATEPOS {oscill_config.math3.gate_position}e-6")
        self.write_cmd(f"MATH3:NUMAvg {oscill_config.math_averages}")

    def _update_math3_cont(self):
        oscill_config = self.config.oscilloscope_controller
        self.write_cmd("SELECT:MATH4 0")
        self.write_cmd(f'MATH3:DEFINE "SpectralMag({self.channel})"')
        self.write_cmd("SELECT:MATH3 1")

        self.write_cmd(f"MATH3:SPECTral:WINdow {oscill_config.math3_cont.window}")
        self.write_cmd(f"MATH3:SPECTral:RESBw {oscill_config.math3_cont.resolution}e3")
        self.write_cmd("MATH3:SPECTral:CENTER 30E6")
        self.write_cmd(
            f"MATH3:SPECTral:GATEPOS {oscill_config.math3_cont.gate_position}e-6"
        )
        self.write_cmd(f"MATH3:NUMAvg {oscill_config.math_averages}")
        self.write_cmd("MATH3:VERTICAL:SCALE 5E-3")

        self.start_acq()

    def _update_math4(self):
        oscill_config = self.config.oscilloscope_controller
        self.write_cmd("SELECT:MATH3 0")
        self.write_cmd(f'MATH4:DEFINE "SpectralMag(AVG({self.channel}))"')
        self.write_cmd("SELECT:MATH4 1")
        self.write_cmd(f"MATH4:SPECTral:WINdow {oscill_config.math4.window}")
        self.write_cmd(f"MATH4:SPECTral:RESBw {oscill_config.math4.resolution}e3")
        self.write_cmd(f"MATH4:SPECTral:GATEPOS {oscill_config.math4.gate_position}e-6")
        self.write_cmd(f"MATH4:NUMAvg {oscill_config.math_averages}")

