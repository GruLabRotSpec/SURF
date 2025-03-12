import time
import pyvisa as visa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
import zaberController, SRScontroller, valonController, oscilloscopeController
from scipy.signal import find_peaks
import os

# This code is meant to scan the whole region from 0 - 40 mm and find all the cavity positions for a set frequency

def initializeInstruments():
    global valonConnect
    try:
        oscilloscopeController.initializeScope()
        SRScontroller.initializeSRS()
        zaberController.initializeZaber()
        valonConnect = valonController.initializeValon('COM3')
        valonController.valonSettings()
    except PermissionError:
        print("ATTN: Permission Error. Make sure Zaber window is closed.")

def DefineParameters():
    global directory,rundirectory, filename, valonFreq,awgFreq, StepSize, stepUpVar, StopFreqVar, StopFreq
    awgFreq = 30
    totalFreq = float(input("Starting TOTAL (AWG INCLUDED, THIS SUBTRACTS IT FOR YOU) frequency? (MHz): "))
    valonFreq = totalFreq - awgFreq
    valonController.writeValonCommand(f"Frequency {valonFreq} MHz")
    oscilloscopeController.recallsetup('cavity_ch2000001.set')

    k = 0
    folderpath = 'Cavity Scan'
    filename = input('What name to add to file? : ')

    # creating directory for files to be

    if not os.path.exists(f'{folderpath}/{filename}_{k}'):
        os.makedirs(f'{folderpath}/{filename}_{k}')
        os.makedirs(f'{folderpath}/{filename}_{k}/CavityRuns')
        print('folder for data has been created: ', f'{folderpath}/{filename}_{k}')
    else:
        while os.path.exists(f'{folderpath}/{filename}_{k}'):
            k += 1
        os.makedirs(f'{folderpath}/{filename}_{k}')
        os.makedirs(f'{folderpath}/{filename}_{k}/CavityRuns')
        print('folder for data has been created: ', f'{folderpath}/{filename}_{k}')

    directory = f"{folderpath}/{filename}_{k}"
    rundirectory = f'{folderpath}/{filename}_{k}/CavityRuns'

    if not os.path.exists(f'{directory}/{filename}.csv'):
        open(f'{directory}/{filename}.csv', 'w+')
        print('Sucessfully named file ', f'{directory}/{filename}.csv')
        
    zaberController.zaberSetSpeed(101204)
    zaberController.homeZaber()
    zaberController.zaberDevice.poll_until_idle()
    
    print('Zaber has arrived at home position 0 mm')
    StepSize = input("Freq step size? (MHz): ")
    StopFreqinput = float(input("What Frequency should the experiment end?: "))
    StopFreq = StopFreqinput - awgFreq
    try:
        StepSize = float(StepSize)
        stepUpVar = True
        valonController.writeValonCommand(f'FrequencyStep {StepSize} MHz')
    except ValueError:
        stepUpVar = False
        print("Only running single sequence.")
    try:
        StopFreq = float(StopFreq)
        StopFreqVar = True
    except ValueError:
        StopFreqVar = False
        print("No end frequency set. ")

    print("All parameters acquired, moving to calibrate and run sequence.")
def CavitySearch():
    global endPosZaber, speedZaber, maxList, timeList
    maxList = []
    timeList = []
    runBool = 'y'
    i = 0

    while runBool == 'y':
        NewFreq = valonFreq + StepSize * i + awgFreq
        print(f'The new Valon Frequency is: {NewFreq}')

        startPosZaberMM = 0
        endPosZaberMM = 40

        startPosZaber = round(startPosZaberMM * 20997.375)
        endPosZaber = round(endPosZaberMM * 20997.375)
        while True:
            try:
                speedZaber = 0.05
                if 3.5 >= speedZaber > 0:
                    totalTime = endPosZaberMM / speedZaber
                    print("Run time is: ", totalTime, " s")
                    speedZaber = round(speedZaber * 34402.099737532773)
                elif speedZaber < 0 or speedZaber > 3.5:
                    raise ValueError
                break
            except ValueError:
                print("Invalid integer. The number must be between 0 and 3.5.")
                
        SRScontroller.setFreq(500)  #trigger rate for cavity search
        zaberController.zaberSetSpeed(101204)
        zaberController.homeZaber()
        
        zaberController.zaberDevice.poll_until_idle()
        currPos = zaberController.zaberDevice.get_position()
        currPos = currPos / 220997
        print('Zaber is at position ', currPos)
        zaberController.zaberSetSpeed(speedZaber)
        
        time.sleep(2)
        oscilloscopeController.oscCalibStart()
        SRScontroller.startTrig()

        threadZaber1 = threading.Thread(target=zaberThread)
        threadAcquire1 = threading.Thread(target=acquireThread)

        threads1 = [threadZaber1, threadAcquire1]

        for threadInstances in threads1:
            threadInstances.start()
        for threadInstances in threads1:
            threadInstances.join()
        SRScontroller.stopTrig()
        oscilloscopeController.oscCalibStop()
        for maxLists in maxList:
            posArr = np.linspace(startPosZaberMM, endPosZaberMM, len(maxLists))
            print("Length of max: ", len(maxLists))
            print("Length of pos: ", len(posArr))

            DF = pd.DataFrame({'Zaber Position (mm)':posArr,"Intensity (Volts)": maxLists, 'Frequency':NewFreq})
            x = DF['Zaber Position (mm)']
            y = DF['Intensity (Volts)']
        
        #threshold = input('Threshold for peak selection (in V): ')
        threshold = 0.008
        peaks, _ = find_peaks(y, height=threshold)
        
        plt.plot(x, y)
        plt.plot(x[peaks], y[peaks], "x")
        plt.title("Zaber Position vs. Intensity")
        plt.xlabel("Zaber Position (mm)")
        plt.ylabel("Intensity (Volts)")
        plt.show(block=False)
        plt.pause(10)
        plt.close()

        df1 = pd.DataFrame({'Zaber Position (mm)':x,'Intensity (V)':y,'Frequency (MHz)':NewFreq})
        df2 = pd.DataFrame({'Peaks':x[peaks],'Intensity':y[peaks]})
        df2 = df2.reset_index(drop=True)
        pd.concat([pd.concat([df1, df2], axis=1)]).to_csv(f'{directory}/{filename}.csv',mode="a", index=False)
        pd.concat([pd.concat([df1, df2], axis=1)]).to_csv(f'{rundirectory}/{NewFreq}MHz.csv',mode="w+", index=False)


        print('run #', i + 1, 'has been added to: ', f'{directory}/{filename}.csv')
        

       # SRScontroller.stopTrig()
        #oscilloscopeController.oscCalibStop()
        if stepUpVar == True and StopFreqVar == True:
            if NewFreq <= StopFreq:
                i += 1
                valonController.valonStepUp()

            else:
                print('You have reached the stop frequency. You will find your data in .csv file: ',
                      f'{directory}/{filename}.csv')
                break

        elif stepUpVar == True and StopFreqVar == False:
            runBool = input("Do you want to run another experiment? (Y/N): ").lower()
            if runBool == "y":
                i += 1
                valonController.valonStepUp()
            if runBool == "n":
                print(f"Experiment concluded. You will find your data in .csv file: ", f'{directory}/{filename}.csv')
                zaberController.homeZaber()
            break

def PeakAnalysis():
    pass

def zaberThread():
    global loopVar
    loopVar = 1
    timeZaberStart = time.perf_counter()
    totalTime = zaberController.zaberStart(speedZaber)
    zaberController.zaberDevice.move_abs(endPosZaber)
    zaberController.zaberDevice.poll_until_idle()
    timeZaberEnd = time.perf_counter()
    currPos = zaberController.zaberDevice.get_position()
    print("Zaber is at end position: ", currPos / 20997, " mm")
    totalTimeZaber = timeZaberEnd - timeZaberStart
    print("Zaber move time (s): ", totalTimeZaber)
    loopVar = 0
    timeList.append(totalTimeZaber)
    return


#vcurrently doesn't run based on trigFreq, if required then use if/else with time.perfcounter()
def acquireThread():
    global loopVar
    tempMaxList = []
    while loopVar == 1:
        # currently we are not acquiring based on frequency
        tempMaxList.append(float(oscilloscopeController.queryOscCmd('MEASUrement:MEAS1:VALUE?')))       #MEAS2 does the number reference the channel

    maxList.append(tempMaxList)

def main():
    initializeInstruments()
    DefineParameters()
    CavitySearch()


if __name__ == "__main__":
    main()
