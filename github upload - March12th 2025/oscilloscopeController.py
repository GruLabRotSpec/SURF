import time
import pyvisa as visa
import numpy as np

#notes:
#ESR giving command error "5": Command Error. Shows that an error occurred while the
# instrument was parsing a command or query.

visa_address_Scope = 'TCPIP0::169.254.23.223::inst0::INSTR'


#initializing scope
def initializeScope():
    global oscilloScope
    rm = visa.ResourceManager()
    oscilloScope = rm.open_resource(visa_address_Scope)   #delay after each command
    oscilloScope.timeout = 10000 #ms
    oscilloScope.encoding = 'latin_1'
    oscilloScope.write_termination = '\n'
    #oscilloScope.read_termination = '\n'
    oscilloScope.expect_termination=False
    oscilloScope.chunk_size = 102400    # larger data sizes 
    #oscillowriteOscCmd('*rst') #reset
    time.sleep(1)
    r = oscilloScope.query('*opc?') # sync
    print(r)
    oscilloScope.write('*cls')
    print("__________________________")
    print("Scope opened successfully.")
    print("__________________________")
    channel = input('Which scope channel are you using? (EX. CH1): ')   #easily change the input channel

    return oscilloScope


#sends command, ensures no error after
def writeOscCmd(command):
    oscilloScope.write(command)
    errorCheck = oscilloScope.write('*ESR?')
    print(f'Command status register: {errorCheck}')
    oscilloScope.write('*cls')


#query command
def queryOscCmd(command):
    output = oscilloScope.query(f'{command}')
    #print(command, ": ", output)
    return output


#grabParam for generating waveform plot
def grabParam():
    print(queryOscCmd('wfmoutpre:xincr?'))
    timeScale = float(queryOscCmd('wfmoutpre:xincr?'))  #horizontal spacing
    timeStart = float(queryOscCmd('wfmoutpre:xzero?'))
    verticalScale = float(queryOscCmd('wfmoutpre:ymult?')) # volts / level
    verticalOffset = float(queryOscCmd('wfmoutpre:yzero?')) # reference voltage
    verticalPosition = float(queryOscCmd('wfmoutpre:yoff?')) # reference position (level)
    FreqCent= float(queryOscCmd('MATH2:SPECTral:CENTER?'))
    FreqSpan = float(queryOscCmd('MATH2:SPECTral:SPAN?'))
    Resolution = float(queryOscCmd('MATH2:SPECTral:RESBw?'))
    GatePos = float(queryOscCmd('MATH2:SPECTral:GATEPOS?'))
    GateWidth = float(queryOscCmd('MATH2:SPECTral:GATEWIDTH?'))

    print("______________________________")
    print("Parameters acquired from scope")
    print("______________________________")
    return timeScale, timeStart, verticalScale, verticalOffset, verticalPosition, FreqCent, FreqSpan, Resolution, GatePos, GateWidth


#starts oscilloscope run
def oscCalibStart():
    # initial config
    writeOscCmd('acquire:state 0')
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRIBINARY')
    writeOscCmd('data:source CH1') # channel
    writeOscCmd('wfmoutpre:byt_n 1') # 1 byte per sample

    # acq config
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:STOPAfter RUNSTop') # cont
    writeOscCmd('acquire:state 1')


#stops oscilloscope run
def oscCalibStop():
    writeOscCmd('acquire:state 0')


def clearOsc():
    writeOscCmd("CLEAR ALL")    #doesn't work


def oscRunScope():
    writeOscCmd('acquire:state 1') # run


#gas pulse acquisition
def acquireFFTDataAtMax(awgFreq, setup):           
    #math4 input param
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:source MATH2')  # channel
    writeOscCmd('wfmoutpre:byt_nr 4')
    recallsetup(setup)
    
    # io config
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:start 1') # first sample
    recordLength = int(queryOscCmd('horizontal:recordlength?'))
    writeOscCmd('data:stop {}'.format(recordLength))                #need to figure out if this is necessary
    writeOscCmd('wfmoutpre:byt_nr 4')

    # acq config
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:STOPAfter RUNSTop') # cont acq
    writeOscCmd('curvestream?')
    writeOscCmd('acquire:state 1') # run

    # data query
 
    t7 = time.perf_counter()
    bin_wave = oscilloScope.query_binary_values('curve?', datatype='f' , container=np.array, is_big_endian=True)
    t8 = time.perf_counter()
    print("acquire time: ", t8-t7)

    writeOscCmd('WFMOutpre?')
    recallsetup(setup)

    return bin_wave

def recallsetup(setup):
    folder = 'C:\Documents and Settings\Administrator\My Documents\Setups_for_lab'
    writeOscCmd(f'RECALL:SETUP "{folder}\{setup}"')
    time.sleep(3)
    print('Successfully recalled setup')


def recallsetupScopeCavity():
    #writeOscCmd('RECALL:SETUP "4MS_cavity000.set"')
    writeOscCmd('RECALL:SETUP "cavity_ch2000002.set"')
    #writeOscCmd('RECALL:SETUP "cavity0917001.set"')
    
    time.sleep(7)

def recallMolPeakScope():
    #writeOscCmd('RECALL:SETUP "091724000.set"')
    #writeOscCmd('RECALL:SETUP "4MS_cavity000.set"')
    #writeOscCmd('RECALL:SETUP "molpeak_nbn000.set"')        #setup for N butynitrile
    writeOscCmd('RECALL:SETUP "cavity000.set"') 
    time.sleep(7)
 #  C:\Documents and Settings\Administrator\My Documents\Setups_for_lab




def acqFTCurve(acqtime):     #this is for actually pulling the data
   
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:source MATH2') # channel
    writeOscCmd('wfmoutpre:byt_nr 4')

    # acq configuration 
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:STOPAfter RUNSTop') # cont acq
    writeOscCmd('curvestream?')
    writeOscCmd('acquire:state 1') # run

    # data query
    time.sleep(acqtime)
    t7 = time.perf_counter()
    new_bin_wave = oscilloScope.query_binary_values('curve?', datatype='f', container=np.array, is_big_endian=True)
    t8 = time.perf_counter()
    print("acquire time: ", t8-t7)

    writeOscCmd('WFMOutpre?')
    print(new_bin_wave)

    return new_bin_wave


####################################################################################################################
#establish settings for ANY WF acquisition
# def estabOscSettings():             ###     Not currently being used
#     global channel, horScale, sampleRate, termination, vScale, triggerLvl
#
#     #hardcoding settings [for now]
#     channel = 'CH1'
#     horScale = '5E-6'
#     sampleRate = '100E+6'
#     termination = '50E+0'
#     vScale = '400E-6'
#     triggerLvl = '60E-03'
#     triggerSource = 'CH1'
#
#     writeOscCmd(f'HORizontal:MODE:SCAle {horScale}') #horizontal scale, each div (*10)
#     #writeOscCmd('HORizontal:MODE:RECOrdlength 20E+3')
#     writeOscCmd(f'HORizontal:MODE:SAMPLERate {sampleRate}') #sampling rate, sample rate * hor. scale = RL
#     writeOscCmd(f'MASK:MASKPRE:VSCAle {vScale}')
#     writeOscCmd(f'{channel}:TERmination {termination}') #50E+0 vs 1E+0
#     writeOscCmd(f"{channel}:BANdwidth:ENHanced OFF")
#     writeOscCmd(f'{channel}:BANdwidth TWOfifty')
#     writeOscCmd(f'{channel}:COUPling DC') #
#     writeOscCmd(f'TRIGger:A:LEVel {triggerLvl}') #fixes trigger level
#     writeOscCmd(f'TRIGGER:A:EDGE:SOURCE {triggerSource}') #sets trigger source
#
#
# def estabMAXSettings(awgFreq):
#     #setting up ch1
#     recallsetupScopeCavity()
#
#     #cursor code
#     writeOscCmd("CURSOR:STATE ON")
#     writeOscCmd("CURSor:SOUrce1 MATH3")
#     writeOscCmd("CURSor:SOURce2 MATH3")
#     writeOscCmd(f"CURSor:VBArs:POS1 {awgFreq - 0.1}E+6") #cursor 1
#     writeOscCmd(f"CURSor:VBArs:POS2 {awgFreq + 0.1}E+6") #cursor 2
#     writeOscCmd("CURSOR:STATE ON")
#     print(queryOscCmd("CURSor?"))
#
#     #max set code
#     writeOscCmd('MEASUREMENT:MEAS1:SOURCE1 MATH3')
#     writeOscCmd('MEASUrement:MEAS1:TYPe MAXimum')
#     #writeOscCmd('MEASUrement:MEAS1:STATE ON')
#
#
# def contAcqMAX():
#     writeOscCmd('header 0')
#     writeOscCmd('data:encdg SRIBINARY')
#     writeOscCmd('data:source CH1')
#     writeOscCmd('wfmoutpre:byt_n 1')