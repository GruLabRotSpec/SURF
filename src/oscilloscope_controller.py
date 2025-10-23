import time
import pyvisa as visa
import numpy as np

VISUAL_ADRESS_SCOPE = "TCPIP0::169.254.23.223::inst0::INSTR"


class Oscilloscope:
    # initializing scope
    def __init__(self):
        rm = visa.ResourceManager()
        self.oscilloScope = rm.open_resource(VISUAL_ADRESS_SCOPE)  # delay after each command
        self.oscilloScope.timeout = 10000  # ms
        self.oscilloScope.encoding = "latin_1"
        self.oscilloScope.write_termination = "\n"
        # oscilloScope.read_termination = '\n'
        self.oscilloScope.expect_termination = False
        self.oscilloScope.chunk_size = 102400  # larger data sizes
        # oscillowriteOscCmd('*rst') #reset
        time.sleep(1)
        r = self.oscilloScope.query("*opc?")  # sync
        print(r)
        self.oscilloScope.write("*cls")

    # sends command, ensures no error after
    def writeOscCmd(self, command):
        self.oscilloScope.write(command)
        errorCheck = self.oscilloScope.write("*ESR?")

        # ESR giving command error "5": Command Error. Shows that an error occurred while the
        # instrument was parsing a command or query.
        if errorCheck != 6:
            print(f"Command status register error: {errorCheck}")

        self.oscilloScope.write("*cls")

    # query command
    def queryOscCmd(self, command):
        output = self.oscilloScope.query(f"{command}")
        # print(command, ": ", output)
        return output

    # grabParam for generating waveform plot
    def grabParam(self):
        timeScale = float(self.queryOscCmd("wfmoutpre:xincr?"))  # horizontal spacing
        timeStart = float(self.queryOscCmd("wfmoutpre:xzero?"))
        verticalScale = float(self.queryOscCmd("wfmoutpre:ymult?"))  # volts / level
        verticalOffset = float(self.queryOscCmd("wfmoutpre:yzero?"))  # reference voltage
        verticalPosition = float(self.queryOscCmd("wfmoutpre:yoff?"))  # reference position (level)

        FreqCent = float(self.queryOscCmd("MATH4:SPECTral:CENTER?"))
        FreqSpan = float(self.queryOscCmd("MATH4:SPECTral:SPAN?"))
        Resolution = float(self.queryOscCmd("MATH4:SPECTral:RESBw?"))
        GatePos = float(self.queryOscCmd("MATH4:SPECTral:GATEPOS?"))
        GateWidth = float(self.queryOscCmd("MATH4:SPECTral:GATEWIDTH?"))

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
    def oscCalibStart(self):
        # initial config
        self.writeOscCmd("acquire:state 0")
        self.writeOscCmd("header 0")
        self.writeOscCmd("data:encdg SRIBINARY")
        self.writeOscCmd("data:source CH1")  # channel
        self.writeOscCmd("wfmoutpre:byt_n 1")  # 1 byte per sample

        # acq config
        self.writeOscCmd("acquire:state 0")  # stop
        self.writeOscCmd("acquire:STOPAfter RUNSTop")  # cont
        self.writeOscCmd("acquire:state 1")

    # stops oscilloscope run
    def oscCalibStop(self):
        self.writeOscCmd("acquire:state 0")

    def clearOsc(self):
        self.writeOscCmd("CLEAR ALL")  # doesn't work

    def oscRunScope(self):
        self.writeOscCmd("acquire:state 1")  # run

    def acquireFFTDataAtMax(self):
        # math4 input param
        self.writeOscCmd("header 0")
        self.writeOscCmd("data:encdg SRPbinary")
        self.writeOscCmd("data:source MATH4")  # channel
        self.writeOscCmd("wfmoutpre:byt_nr 4")

        # io config
        self.writeOscCmd("header 0")
        self.writeOscCmd("data:encdg SRPbinary")
        self.writeOscCmd("data:start 1")  # first sample
        self.writeOscCmd("wfmoutpre:byt_nr 4")

        # acq config
        self.writeOscCmd("acquire:state 0")  # stop
        self.writeOscCmd("acquire:STOPAfter RUNSTop")  # cont acq
        self.writeOscCmd("curvestream?")
        self.writeOscCmd("acquire:state 1")  # run

        # data query
        t7 = time.perf_counter()
        bin_wave = self.oscilloScope.query_binary_values(
            "curve?", datatype="f", container=np.array, is_big_endian=True
        )
        t8 = time.perf_counter()
        print("acquire time: ", t8 - t7)

        self.writeOscCmd("WFMOutpre?")

        return bin_wave

    def recallsetup(self, setup):
        # TODO: This probably should not be hardcoded
        folder = "C:\\Documents and Settings\\Administrator\\My Documents\\Setups_for_lab"
        self.writeOscCmd(f'RECALL:SETUP "{folder}\\{setup}"')
        time.sleep(3)
        print("Successfully recalled setup")

    def recallsetupScopeCavity(self):
        # writeOscCmd('RECALL:SETUP "4MS_cavity000.set"')
        self.writeOscCmd('RECALL:SETUP "cavity_ch2000002.set"')
        # writeOscCmd('RECALL:SETUP "cavity0917001.set"')

        time.sleep(7)

    def recallMolPeakScope(self):
        # writeOscCmd('RECALL:SETUP "091724000.set"')
        # writeOscCmd('RECALL:SETUP "4MS_cavity000.set"')
        # writeOscCmd('RECALL:SETUP "molpeak_nbn000.set"')        #setup for N butynitrile
        self.writeOscCmd('RECALL:SETUP "cavity000.set"')
        time.sleep(7)

    def acqFTCurve(self, channel, acqtime):  # this is for actually pulling the data
        self.writeOscCmd("header 0")
        self.writeOscCmd("data:encdg SRPbinary")
        self.writeOscCmd("data:source MATH4")  # channel
        self.writeOscCmd("wfmoutpre:byt_nr 4")

        # acq configuration
        self.writeOscCmd("acquire:state 0")  # stop
        self.writeOscCmd("acquire:STOPAfter RUNSTop")  # cont acq
        self.writeOscCmd("curvestream?")
        self.writeOscCmd("acquire:state 1")  # run
        self.writeOscCmd(f"{channel}:SCAle 0.9")

        # data query
        time.sleep(acqtime)
        t7 = time.perf_counter()
        new_bin_wave = self.oscilloScope.query_binary_values(
            "curve?", datatype="f", container=np.array, is_big_endian=True
        )
        t8 = time.perf_counter()
        print("acquire time: ", t8 - t7)

        self.writeOscCmd("WFMOutpre?")

        return new_bin_wave

    def SetScopeSettings(self, channel, gatepos):
        self.writeOscCmd("SELECT:MATH3 0")
        self.writeOscCmd("SELECT:MATH4 1")

        self.writeOscCmd(f'MATH4:DEFINE "SpectralMag(AVG({channel}))"')
        self.writeOscCmd("MATH4:NUMAvg 1000000")
        self.writeOscCmd("MATH4:VERTical:POSition -4")
        self.writeOscCmd("MATH4:SPECTral:WINdow Hanning")
        self.writeOscCmd("HORizontal:MODE:SAMPLERate 500E6")
        self.writeOscCmd("HORizontal:MODE:SCAle 5E-6")
        self.writeOscCmd("MATH4:SPECTral:RESBw 100E3")
        self.writeOscCmd("MATH4:SPECTral:CENTER 30E6")
        self.writeOscCmd("MATH4:SPECTral:SPAN 20E6")
        self.writeOscCmd(f"MATH4:SPECTral:GATEPOS {gatepos}")
        self.writeOscCmd("MATH4:VERTICAL:SCALE 500E-6")  # sets math channel vertical scale
        time.sleep(2)
        self.writeOscCmd(f"{channel}:SCAle 1")

    def SetScopeTuningSettings(self, channel):
        self.writeOscCmd("SELECT:MATH4 0")
        self.writeOscCmd("SELECT:MATH3 1")
        self.writeOscCmd(f'MATH3:DEFINE "SpectralMag({channel})"')

        self.writeOscCmd("MATH3:SPECTral:WINdow KAISERBessel")
        self.writeOscCmd("MATH3:VERTical:POSition -4")
        self.writeOscCmd("HORizontal:MODE:SAMPLERate 100E6")
        self.writeOscCmd("HORizontal:MODE:SCAle 500E-9")
        self.writeOscCmd("MATH3:SPECTral:RESBw 835E3")
        self.writeOscCmd("MATH3:SPECTral:CENTER 30E6")
        self.writeOscCmd(f"MATH3:SPECTral:GATEPOS 1E-6")
        self.writeOscCmd("MATH3:VERTICAL:SCALE 5E-3")  # sets math channel vertical scale

        self.oscCalibStart()
