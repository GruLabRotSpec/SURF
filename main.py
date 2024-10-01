import time
import pyvisa as visa
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
import valonController, oscilloscopeController, zaberController, SRScontroller
import os
import csv



def initializeInstruments():
    global valonConnect
    try:
        oscilloscopeController.initializeScope()
        SRScontroller.initializeSRS()
        valonConnect = valonController.initializeValon('COM3')
        valonController.valonSettings()
        zaberController.initializeZaber()
    except PermissionError:
        print("ATTN: Permission Error. Make sure Valon and Zaber windows are closed.")

def setParameters():
    global awgFreq, totalFreq, valonFreq, StepSize, stepUpVar, StopFreq, StopFreqVar, directory,filename
    
    #awgFreq = float(input("What is the AWG frequency? (EX: 30 if 30mHz): ")) for inputing awgFreq
    k = 0 
    folderpath ='Cavity Files'
    filename = input('What name to add to file? : ')

    # creating directory for files to be

    if not os.path.exists(f'{folderpath}/{filename}_{k}'):
        os.makedirs(f'{folderpath}/{filename}_{k}')
        print('folder for data has been created: ', f'{folderpath}/{filename}_{k}')
    else:
        while os.path.exists(f'{folderpath}/{filename}_{k}'):
            k+=1
        os.makedirs(f'{folderpath}/{filename}_{k}')
        print('folder for data has been created: ', f'{folderpath}/{filename}_{k}')
    
    
    directory = f"{folderpath}/{filename}_{k}"

    
    if not os.path.exists(f'{directory}/{filename}.csv'):
        
        open(f'{directory}/{filename}.csv', 'w+')
        print('Sucessfully named file ', f'{directory}/{filename}.csv')

    
    awgFreq = 30
    print("AWG Frequency is set to ", awgFreq, " MHz")

    oscilloscopeController.estabMAXSettings(awgFreq)
    #Valon config
    totalFreq = float(input("Starting TOTAL (AWG INCLUDED, THIS SUBTRACTS IT FOR YOU) frequency? (MHz): "))
    valonFreq = totalFreq - awgFreq
    valonController.writeValonCommand(f"Frequency {valonFreq} MHz")

    #getting freq step if needed
    print("******IF ONLY RUNNING ONCE, ENTER ANYTHING BUT A NUMBER for StepSize and StopFreq")
    StepSize= input("Freq step size? (MHz): ")
    StopFreq = input("What Frequency should the experiment end?: ")
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

def CalibrateAndRun():
    global maxList, timeList, speedZaber,endPosZaber, NewFreq
    maxList = []
    timeList = []
    maxMaxVals = []
    runBool = "y"
    NewFreq = valonFreq
 
    i = 0   # when i = 0 it is the first run
    while runBool=="y":
        if i == 0:
            while True:
                try:
                
                ## For setting the calibration points manually for zaber
                # startPosZaber = float(input("Starting position? (mm): "))
                # endPosZaber = float(input("Ending position? (mm): "))
                    travelDistZaber = 4  # mm
                    totalAbsDist = 40
                    # attempt at trying to predict the initial starting and ending positions
                    startPosZaber = ((4.23491632201815e-9 * (totalFreq ** 2)) + (
                    0.00214275759953761 * totalFreq) - 2.05776365002228) - 1  # - estimating start position # double for this since the first val taken out of midpt

                    endPosZaber = travelDistZaber + startPosZaber
                    totalDistZaberMM = endPosZaber - startPosZaber
                # global positions in MM for plotting
                    startPosZaberMM = startPosZaber
                    endDistZaberMM = endPosZaber

                    print("Attempting to travel from ", startPosZaber, "mm to ", endPosZaber, "mm")
                    if endPosZaber <= 40 and startPosZaber <= 40 and endPosZaber >= 0 and startPosZaber >= 0:
                        endPosZaber = round(endPosZaber * 20997.375)
                        startPosZaber = round(startPosZaber * 20997.375)
                        totalAbsDistZaber = round(totalAbsDist*20997.375)
                    elif endPosZaber > 40 and startPosZaber<= 40 and endPosZaber>=0 and startPosZaber>=0:
                            endPosZaber = 40
                            endPosZaber = round(endPosZaber*20997.375)
                            startPosZaber = round(startPosZaber*20997.375)
                    elif endPosZaber < 0  or startPosZaber < 0 or startPosZaber > 40:
                        raise ValueError
                    break
                except ValueError:
                    print("Invalid integers somewhere. The numbers must be between 0 and 40mm.")
                    break
                #setting the speed for the zaber
            print("Attempting to travel from ", startPosZaber/20997.375, "mm to ", endPosZaber/20997.375, "mm")
            while True:
                try:
                    speedZaber = float(input("Set the movement velocity of the Zaber (mm/s, max 3.5 m/s):"))
                    if speedZaber <= 3.5 and speedZaber > 0:
                        totalTime = totalDistZaberMM / speedZaber
                        print("Run time is: ", totalTime, " s")
                        speedZaber = round(speedZaber*34402.099737532773)
                    elif speedZaber < 0 or speedZaber > 3.5:
                        raise ValueError
                    break
                except ValueError:
                 print("Invalid integer. The number must be between 0 and 3.5.")


            totalTime = totalDistZaberMM/speedZaber
          

         #SRS config
            trigFreq = SRScontroller.inputFreq()
        
            #oscilloscopeController.oscCalibStart()          # setting maybe unneccessary settings?
        #zaber movement 
            zaberController.zaberSetSpeed(101204)   #speed for moving to starting position
            startZaber = startPosZaber / 20997
            print(f"Moving Zaber to {startZaber}.")
            zaberController.moveToZaber(startPosZaber)
            zaberController.zaberDevice.poll_until_idle()
            currPos = zaberController.zaberDevice.get_position()        #these two lines are a bit redundant come back and fix
            print("Homing... Zaber is at position: ", currPos/20997)
            zaberController.zaberDevice.poll_until_idle()
            zaberController.zaberSetSpeed(speedZaber)

            

            SRScontroller.startTrig()

            oscilloscopeController.clearOsc()
            

            threadZaber = threading.Thread(target=zaberThread)
            threadAcquire = threading.Thread(target=acquireThread)

            threads = [threadZaber, threadAcquire]

            for threadInstances in threads:
             threadInstances.start()
        
            for threadInstances in threads:
                threadInstances.join()

            oscilloscopeController.oscCalibStop()

            print("acq length: ", len(maxList))

            for maxLists in maxList:
                 posArr = np.linspace(startPosZaberMM, endDistZaberMM, len(maxLists))
                 print("Length of pos: ", len(posArr))
                 print(max(maxLists))
                 plt.plot(posArr, maxLists)
                 plt.title("Zaber Position vs. Intensity")
                 plt.xlabel('Zaber Position (mm)')
                 plt.ylabel('Intensity (Volts)')
                 plt.show(block=False)
                 plt.pause(3)
                 plt.close()
                 print(max(maxLists))
                 
            for items in maxList:
                print("len: ", len(items))
                maxer = max(items)
            for index, values in enumerate(items):
                if values == maxer:
                    print("Max position found: ", posArr[index])
                    peakMax = posArr[index]
                    maxMaxVals.append(peakMax)

            peakMidpt = round((len(maxMaxVals))/2)
            maxPos = maxMaxVals[peakMidpt]
            
            print("Moving to maximum at: ", maxPos, " mm")
            zaberController.zaberSetSpeed(101204)
            zaberController.moveToZaber(int(maxPos*20997))
            zaberController.zaberDevice.poll_until_idle()
            currPos = zaberController.zaberDevice.get_position()
            print("Running scan...Zaber is at position: ", currPos/20997)
            SRScontroller.stopTrig()
            
            SRScontroller.startPulse()
            
            SRScontroller.setTrig(5)
          
          
            getWave(awgFreq)
            xxValues,yyValues = fftFromScope()
           

            
            oscilloscopeController.oscCalibStop()   #see if this changes anything
    
            SRScontroller.stopPulse()
            oscilloscopeController.clearOsc()
            
            DF1 = pd.DataFrame({'Frequency (MHz)':xxValues,'Intensity':yyValues}) 

            j=0

            if os.path.exists(f'{directory}/Cavity_Output_{j}.csv'):
                while os.path.exists(f"{directory}/Cavity_Output_{j}.csv"):
                    j += 1
            
            filename_first = f"Cavity_Output_{j}"  
            DF1.to_csv(f'{directory}/{filename_first}.csv',mode='w',index=True)  #Individual run output
            DF1.to_csv(f'{directory}/{filename}.csv', mode = 'a',index=True)     #appends main file
                
    

        else:
            while True:
                try:
                    
                    maxList = []
                    timeList = []
                    maxMaxVals = []
                    oscilloscopeController.estabMAXSettings(awgFreq)
                    time.sleep(5)
                    #oscilloscopeController.recallsetupScopeCavity()
                    NewFreq = valonFreq+StepSize*i
                    print(f'The new Valon Frequency is: {NewFreq}')
                    # to scan 2 mm from the previous max position
                    travelDistZaber=1
                    startPosZaber = maxPos-0.5
                    endPosZaber = travelDistZaber + startPosZaber
                    totalDistZaberMM = endPosZaber - startPosZaber
                    #for plotting
                    startPosZaberMM = startPosZaber
                    endPosZaberMM = endPosZaber
                    

                    print("Attempting to travel from ", startPosZaber, " mm to ", startPosZaber+travelDistZaber, " mm")
                    if endPosZaber <= 40 and startPosZaber <= 40 and endPosZaber >= 0 and startPosZaber >= 0:
                         endPosZaber = round(endPosZaber*20997.375)
                         startPosZaber = round(startPosZaber*20997.375)
                    elif endPosZaber > 40 and startPosZaber<= 40 and endPosZaber>=0 and startPosZaber>=0:
                            endPosZaber = 40
                            endPosZaber = round(endPosZaber*20997.375)
                            startPosZaber = round(startPosZaber*20997.375)
                    elif endPosZaber < 0  or startPosZaber < 0 or startPosZaber > 40:
                        raise ValueError
                    break
                except ValueError:
                    print("Invalid integers somewhere. The numbers must be between 0 and 40mm.")
                    break
                #setting the speed for the zaber
            print("Attempting to travel from ", startPosZaber/20997.375, "mm to ", endPosZaber/20997.375, "mm")
           
            while True:
                try:
                    speedZaber = 0.08
                    if speedZaber <= 3.5 and speedZaber > 0:
                        totalTime = totalDistZaberMM / speedZaber
                        print("Run time is: ", totalTime, " s")
                        speedZaber = round(speedZaber*34402.099737532773)
                    elif speedZaber < 0 or speedZaber > 3.5:
                        raise ValueError
                    break
                except ValueError:
                    print("Invalid integer. The number must be between 0 and 3.5.")
            
            SRScontroller.setFreq(400)
            oscilloscopeController.oscCalibStart()

            zaberController.zaberSetSpeed(101204)   # speed for moving to the beginning spot not the speed
            startZaber1 = startPosZaber/20997
            print(f"Moving Zaber to {startZaber1}")
            zaberController.moveToZaber(startPosZaber)
            zaberController.zaberDevice.poll_until_idle()
            zaberController.zaberSetSpeed(speedZaber)

            
            
            SRScontroller.startTrig()
           
            threadZaber1 = threading.Thread(target=zaberThread)
            threadAcquire1 = threading.Thread(target=acquireThread)

            threads1 = [threadZaber1, threadAcquire1]

            for threadInstances in threads1:
                threadInstances.start()
            for threadInstances in threads1:
                threadInstances.join()

            oscilloscopeController.oscCalibStop()
            
            print("aq length: ", len(maxList))

            for maxLists in maxList:
                posArr1 = np.linspace(startPosZaberMM, endPosZaberMM, len(maxLists))
                print("Length of max: ", len(maxList))
                print("Length of pos: ", len(posArr1))
                print(max(maxLists))
                plt.plot(posArr1, maxLists)
                plt.title("Zaber Position vs. Intensity")
                plt.xlabel("Zaber Position (mm)")
                plt.ylabel("Intensity (Volts)")
                plt.show(block=False)
                plt.pause(3)
                plt.close()

            for items in maxList:
                print("len: ", len(items))
                maxer = max(items)
                for index, values in enumerate(items):
                    if values == maxer:
                        print("Max position found: ", posArr1[index])
                        peakMax = posArr1[index]
                        maxMaxVals.append(peakMax)
            
            peakMidpt1 = round(len(maxMaxVals)/2)
            maxPos = maxMaxVals[peakMidpt1]
            plt.close()
            print("Moving to maximum position at: ", maxPos, " mm")
            zaberController.zaberSetSpeed(101204)
            zaberController.moveToZaber(int(maxPos*20997))
            zaberController.zaberDevice.poll_until_idle()
            currPos = zaberController.zaberDevice.get_position()
            print("Running scan... Zaber is at position: ", currPos/20997)

            
            SRScontroller.stopTrig()
            
            SRScontroller.setTrig(5)
            oscilloscopeController.recallMolPeakScope()
            SRScontroller.startPulse()
            
            getWave(awgFreq)
        
            xxValues1,yyValues1=fftFromScope()
            oscilloscopeController.oscCalibStop()
            SRScontroller.stopPulse()
            
            
            DF1 = pd.DataFrame({'Frequency (MHz)':xxValues1,'Intensity':yyValues1})
            
            
            #for naming subsequent runs

            j = 0

            if os.path.exists(f'{directory}/Cavity_Output{j}.csv'):
                while os.path.exists(f"{directory}/Cavity_Output{j}.csv"):
                    j += 1   
            
            filename_add = f"Cavity_Output{j}"
                
            DF1.to_csv(f'{directory}/{filename_add}.csv',index=True)
            DF1.to_csv(f'{directory}/{filename}.csv',mode= 'a',index=True)
            print('run #', i+1,'has been added to: ', f'{directory}/{filename}.csv')


        if stepUpVar == True and StopFreqVar == True:
            if NewFreq <= StopFreq:
                i+=1
                valonController.valonStepUp()
                
            else:
                print('You have reached the stop freqency. You will find your data in .csv file: ', f'{directory}/{filename}.csv')
        if stepUpVar == True and StopFreqVar ==False :
            runBool = input("Do you want to run another experiment? (Y/N): ").lower()
            if runBool == "y":
                i+=1
                valonController.valonStepUp()
            if runBool == "n":
                print(f"Experiment concluded. You will find your data in .csv file: ", f'{directory}/{filename}.csv' )


    
 

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
        tempMaxList.append(float(oscilloscopeController.queryOscCmd('MEASUrement:MEAS1:VALUE?')))

    maxList.append(tempMaxList)


def fftFromScope():
    global timeScale, timeStart, verticalScale, verticalOffset, verticalPosition, FreqCent, FreqSpan

    waveValues = oscilloscopeController.recallsetup_fftdataatmax()
    
    timeScale, timeStart, verticalScale, verticalOffset, verticalPosition, FreqCent, FreqSpan = oscilloscopeController.grabParam()

    
    #oscilloscopeController.writeOscCmd(f'SAVE:WAVEFORM MATH4, "E:\Cavity Data/{filename}.CSV"') #can add in the second folder when actually doing experiments 

    # acquire vals
    xValues, yValues = scaleFFT(waveValues)

    generatePlot(xValues, yValues)

    return xValues,yValues



def scaleWave(waveValues):
    unscaled_wave = np.array(waveValues, dtype='float')
    scaled_wave = (unscaled_wave - verticalPosition) * verticalScale + verticalOffset
    return scaled_wave

def generatePlot(xWave, yWave):
    plt.plot(xWave, yWave)
    plt.title("Data")
    plt.xlabel("Frequency")
    plt.ylabel("Relative Intensity")
    plt.show(block=False)
    plt.pause(3)
    plt.close()
    return

def getWave(awgFreq):
    getWave = oscilloscopeController.acquireFFTDataAtMax(awgFreq)
    return getWave

def getWaveValues(awgFreq):
    getWaveValues = oscilloscopeController.acquireFFTDataAtMax(awgFreq)
    return getWaveValues

def scaleFFT(waveValues):
    valonFreqadd=(NewFreq+awgFreq)*1000000
    horStart = valonFreqadd - (FreqSpan/2)
    horEnd = valonFreqadd + (FreqSpan/2)
    
    fftYValues = np.array(waveValues, dtype='float')
    fftXValues = np.linspace(start=horStart,num=len(waveValues), stop=horEnd)/1000000      
   
    return fftXValues, fftYValues


def main():
  initializeInstruments()
  setParameters()    
  CalibrateAndRun()


if __name__ == "__main__":
    main()


