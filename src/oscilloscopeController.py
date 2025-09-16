import time
import pyvisa as visa
import numpy as np
import os

#notes:
#ESR giving command error "5": Command Error. Shows that an error occurred while the
# instrument was parsing a command or query.

visa_address_Scope = 'TCPIP0::169.254.23.223::inst0::INSTR'

#os.add_dll_directory('C:\\Windows\\system32\\visa64.dll')
#initializing scope
def initializeScope():
    global oscilloScope
    #rm = visa.ResourceManager(r'C:\Windows\System32\visa64.dll')

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
    #channel = input('Which scope channel are you using? (EX. CH1): ')   #easily change the input channel

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
    FreqCent= float(queryOscCmd('MATH4:SPECTral:CENTER?'))
    FreqSpan = float(queryOscCmd('MATH4:SPECTral:SPAN?'))
    Resolution = float(queryOscCmd('MATH4:SPECTral:RESBw?'))
    GatePos = float(queryOscCmd('MATH4:SPECTral:GATEPOS?'))
    GateWidth = float(queryOscCmd('MATH4:SPECTral:GATEWIDTH?'))
    print(timeScale)
    print(timeStart)
    print(FreqCent)
    print(FreqSpan)
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

def acquireFFTDataAtMax():           
    #math4 input param
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:source MATH4')  # channel
    writeOscCmd('wfmoutpre:byt_nr 4')
 
    # io config
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:start 1') # first sample
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

    return bin_wave

#gas pulse acquisition
#def acquireFFTDataAtMax():           
    #math4 input param
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:source MATH2')  # channel
    writeOscCmd('wfmoutpre:byt_nr 4')
    
    # io config
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:start 1') # first sample
    # recordLength = int(queryOscCmd('horizontal:recordlength?'))
    # writeOscCmd('data:stop {}'.format(recordLength))                #need to figure out if this is necessary
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
    # print("acquire time: ", t8-t7)

    writeOscCmd('WFMOutpre?')
   

    return bin_wave

def recallsetup(setup):
    folder = 'C:\\Documents and Settings\\Administrator\\My Documents\\Setups_for_lab'
    writeOscCmd(f'RECALL:SETUP "{folder}\\{setup}"')
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




def acqFTCurve(channel,acqtime):     #this is for actually pulling the data
   
   
    writeOscCmd('header 0')
    writeOscCmd('data:encdg SRPbinary')
    writeOscCmd('data:source MATH4') # channel
    writeOscCmd('wfmoutpre:byt_nr 4')

    # acq configuration 
    writeOscCmd('acquire:state 0') # stop
    writeOscCmd('acquire:STOPAfter RUNSTop') # cont acq
    writeOscCmd('curvestream?')
    writeOscCmd('acquire:state 1') # run
    writeOscCmd(f'{channel}:SCAle 0.9')

    # data query
    time.sleep(acqtime)
    t7 = time.perf_counter()
    new_bin_wave = oscilloScope.query_binary_values('curve?', datatype='f', container=np.array, is_big_endian=True)
    t8 = time.perf_counter()
    print("acquire time: ", t8-t7)

    writeOscCmd('WFMOutpre?')


    return new_bin_wave

def SetScopeSettings(channel, gatepos):
    writeOscCmd('SELECT:MATH3 0')
    writeOscCmd('SELECT:MATH4 1')

    writeOscCmd(f'MATH4:DEFINE "SpectralMag(AVG({channel}))"')
    writeOscCmd('MATH4:NUMAvg 1000000')
    writeOscCmd('MATH4:VERTical:POSition -4')
    writeOscCmd('MATH4:SPECTral:WINdow Hanning')
    writeOscCmd('HORizontal:MODE:SAMPLERate 500E6')
    writeOscCmd('HORizontal:MODE:SCAle 5E-6')
    writeOscCmd('MATH4:SPECTral:RESBw 100E3')
    writeOscCmd('MATH4:SPECTral:CENTER 30E6')
    writeOscCmd('MATH4:SPECTral:SPAN 20E6')
    writeOscCmd(f'MATH4:SPECTral:GATEPOS {gatepos}')
    writeOscCmd('MATH4:VERTICAL:SCALE 500E-6') #sets math channel vertical scale
    time.sleep(2)
    writeOscCmd(f'{channel}:SCAle 1')
    

def SetScopeTuningSettings(channel):

    writeOscCmd('SELECT:MATH4 0')
    writeOscCmd('SELECT:MATH3 1')
    writeOscCmd(f'MATH3:DEFINE "SpectralMag({channel})"')

    writeOscCmd('MATH3:SPECTral:WINdow KAISERBessel')
    writeOscCmd('MATH3:VERTical:POSition -4')
    writeOscCmd('HORizontal:MODE:SAMPLERate 100E6')
    writeOscCmd('HORizontal:MODE:SCAle 500E-9')
    writeOscCmd('MATH3:SPECTral:RESBw 835E3')
    writeOscCmd('MATH3:SPECTral:CENTER 30E6')
    writeOscCmd(f'MATH3:SPECTral:GATEPOS 1E-6')
    writeOscCmd('MATH3:VERTICAL:SCALE 5E-3') #sets math channel vertical scale

    oscCalibStart()

    
