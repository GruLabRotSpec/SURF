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
    global awgFreq, totalFreq, totalFreqStart, valonFreq, StepSize, stepUpVar, StopFreq, StopFreqVar, directory, rundirectory, filename
    
    #awgFreq = float(input("What is the AWG frequency? (EX: 30 if 30mHz): ")) for inputing awgFreq
    k = 0 
    folderpath ='Cavity Data'
    filename = input('What name to add to file? : ')

    # creating directory for files to be

    if not os.path.exists(f'{folderpath}/{filename}_{k}'):
        os.makedirs(f'{folderpath}/{filename}_{k}')
        os.makedirs(f'{folderpath}/{filename}_{k}/CavityFiles')
        print('folder for data has been created: ', f'{folderpath}/{filename}_{k}')
    else:
        while os.path.exists(f'{folderpath}/{filename}_{k}'):
            k+=1
        os.makedirs(f'{folderpath}/{filename}_{k}')
        os.makedirs(f'{folderpath}/{filename}_{k}/CavityFiles')
        print('folder for data has been created: ', f'{folderpath}/{filename}_{k}')
    
    
    directory = f"{folderpath}/{filename}_{k}"
    rundirectory = f'{folderpath}/{filename}_{k}/CavityFiles'
    
    if not os.path.exists(f'{directory}/{filename}.csv'):
        
        open(f'{directory}/{filename}.csv', 'w+')
        print('Sucessfully named file ', f'{directory}/{filename}.csv')

    
    awgFreq = 30
    print("AWG Frequency is set to ", awgFreq, " MHz")

    oscilloscopeController.recallMolPeakScope()
    #Valon config
    totalFreq = float(input("Starting TOTAL (AWG INCLUDED, THIS SUBTRACTS IT FOR YOU) frequency? (MHz): "))
    totalFreqStart = totalFreq + 0.5
    valonFreq = totalFreqStart - awgFreq
    valonController.writeValonCommand(f"Frequency {valonFreq} MHz")

    #getting freq step if needed
    print("******IF ONLY RUNNING ONCE, ENTER ANYTHING BUT A NUMBER for StepSize and StopFreq")
    StepSize= input("Freq step size? (MHz): ")
    StopFreqinput = float(input("What Frequency should the experiment end?: "))
    StopFreq= StopFreqinput - awgFreq
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
            currPos = zaberController.zaberDevice.get_position()
            currPos = currPos/20997
            print('Zaber is at position', currPos)
            Intensity=input('What is the intensity of the found cavity position: ')   
            
            SRScontroller.startPulse()
            
            SRScontroller.setTrig(5)
          
          
            getWave(awgFreq)
            xxValues,yyValues = fftFromScope()

    
            SRScontroller.stopPulse()
            oscilloscopeController.clearOsc()
            oscilloscopeController.oscCalibStop()
            
            DF1 = pd.DataFrame({'Frequency (MHz)':xxValues,'Intensity':yyValues})
            DF2 = pd.DataFrame({'Center Freq': [totalFreqStart], 'Cavity Position':[currPos],'Intensity of Cavity':[Intensity]})

            DF = [DF1,DF2]
            DFcombine = pd.concat(DF,axis=1)

            j = 0

  
            DFcombine.to_csv(f'{rundirectory}/{totalFreqStart}MHz.csv',mode='w',index=False)  #Individual run output
            DFcombine.to_csv(f'{directory}/{filename}.csv', mode = 'a',index=False)     #appends main file
                
    

        else:
            while True:
                try:
                    
                    maxList = []
                    timeList = []
                    maxMaxVals = []
                    #oscilloscopeController.estabMAXSettings(awgFreq)
                    #oscilloscopeController.recallsetupScopeCavity()
                    time.sleep(5)
                    
                    NewFreq = valonFreq+StepSize*i
                    TotalFrequency = NewFreq + awgFreq
                    print(f'The new Valon Frequency is: {NewFreq}')
                    currPos = zaberController.zaberDevice.get_position()
                    # to scan 1 mm from the previous max position
                    #travelDistZaber = 0.6
                    startPosZaber = (currPos / 20997 - 0.2)
                    endPosZaber = startPosZaber + 0.5
                    totalDistZaberMM = endPosZaber - startPosZaber
                    #for plotting
                    startPosZaberMM = startPosZaber
                    endPosZaberMM = endPosZaber
                    

                    print("Attempting to travel from ", startPosZaber, " mm to ", endPosZaber, " mm")
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
            
           
            while True:
                try:
                    speedZaber = 0.01
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
           
            

            zaberController.zaberSetSpeed(101204)   # speed for moving to the beginning spot not the speed
            startZaber1 = startPosZaber/20997
            print(f"Moving Zaber to {startZaber1}")
            zaberController.moveToZaber(startPosZaber)
            zaberController.zaberDevice.poll_until_idle()
            zaberController.zaberSetSpeed(speedZaber)
            oscilloscopeController.recallsetupScopeCavity()
            time.sleep (2)
            oscilloscopeController.oscCalibStart()
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
                maxIntensity = max(maxLists)
                print(max(maxLists))
                plt.plot(posArr1, maxLists)
                plt.title("Zaber Position vs. Intensity")
                plt.xlabel("Zaber Position (mm)")
                plt.ylabel("Intensity (Volts)")
                plt.show(block=False)
                plt.pause(10)
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

            #maxPos = round(maxPos)
            
            SRScontroller.stopTrig()
            
            SRScontroller.setTrig(5)

            SRScontroller.startPulse()
            
            getWave(awgFreq)
        
            xxValues1,yyValues1=fftFromScope()
            oscilloscopeController.oscCalibStop()
            SRScontroller.stopPulse()
            
            # Individual file
            DF1 = pd.DataFrame({'Frequency (MHz)':xxValues1,'Intensity':yyValues1,})
            DF2 = pd.DataFrame({'Center Frequency':TotalFrequency,'Cavity Position':[maxPos],'Intensity of Cavity':[maxIntensity]})

            DF = [DF1,DF2]
            DFcombine = pd.concat(DF,axis=1)
            
            #for naming subsequent runs

                
            DFcombine.to_csv(f'{rundirectory}/{TotalFrequency}MHz.csv',index=False)
            DFcombine.to_csv(f'{directory}/{filename}.csv',mode= 'a',index=False, header=False)
            print('run #', i+1,'has been added to: ', f'{directory}/{filename}.csv')


        if stepUpVar == True and StopFreqVar == True:
            if NewFreq <= StopFreq:
                i+=1
                valonController.valonStepUp()
                
            else:
                print('You have reached the stop frequency. You will find your data in .csv file: ', f'{directory}/{filename}.csv')
                break
        elif stepUpVar == True and StopFreqVar ==False :
            runBool = input("Do you want to run another experiment? (Y/N): ").lower()
            if runBool == "y":
                i+=1
                valonController.valonStepUp()
            if runBool == "n":
                print(f"Experiment concluded. You will find your data in .csv file: ", f'{directory}/{filename}.csv' )
                break


    
 

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


