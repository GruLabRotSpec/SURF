import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
import os

from valon_controller import ValonController
from delay_generator_controller import DelayGeneratorController
from zaber_controller import ZaberController
from oscilloscope_controller import OscilloscopeController
import Cavity
import plot as plotter


####################This version of the code is for the GUI or when not wanting code prompted inputs
###### Inputs manual
# Valon Inputs

RFLevel = 12  # dbm
totalFreq = 8550  # all frequencies should include the awg frequency so no need to subtract
StopFreqinput = 8552
stepsize = 1
StepDirection = "up"  # up or down
# Zaber Inputs
speedZaber = 0.003  # speed for scanning in mm/s

# parameters for code to know, but are not instrument inputs
awgFreq = 30
Intensity = 0.2  # intensity of starting cavity position (V)
gatepos = "18.45E-6"
# Experiment Inputs
acqs = 300
trigRate = 5
# setup = 'cavity_scan_peak001.set'
filename = "4MS_8550_8650MHz_11_12_25"
channel = "CH4"  # oscilloscope channel, doesn't change often but sometimes


def initializeInstruments():
    global valon
    global zaber
    global cavity
    global oscilloscope
    global dgc
    try:
        zaber = ZaberController(speedZaber)
        oscilloscope = OscilloscopeController()
        dgc = DelayGeneratorController()
        valon = ValonController("COM3")

        valon.set_settings(RFLevel)

        cavity = Cavity.Cavity(zaber, oscilloscope, dgc)
        # response = MyPTE1.Connect()
        # print(response)
    except PermissionError:
        print("ATTN: Permission Error. Make sure Valon and Zaber windows are closed.")
        exit()


def setParameters():
    global valonFreq, directory, rundirectory, stepUpVar, StopFreqVar, StopFreq, StepSize, timedelay

    ########## creating directory for files to be
    k = 0
    folderpath = "Cavity Data"

    if not os.path.exists(f"{folderpath}/{filename}_{k}"):
        os.makedirs(f"{folderpath}/{filename}_{k}")
        os.makedirs(f"{folderpath}/{filename}_{k}/CavityFiles")
        print("folder for data has been created: ", f"{folderpath}/{filename}_{k}")
    else:
        while os.path.exists(f"{folderpath}/{filename}_{k}"):
            k += 1
        os.makedirs(f"{folderpath}/{filename}_{k}")
        os.makedirs(f"{folderpath}/{filename}_{k}/CavityFiles")
        print("folder for data has been created: ", f"{folderpath}/{filename}_{k}")

    directory = f"{folderpath}/{filename}_{k}"
    rundirectory = f"{folderpath}/{filename}_{k}/CavityFiles"

    if not os.path.exists(f"{directory}/{filename}.csv"):
        open(f"{directory}/{filename}.csv", "w+")
        print("Successfully named file ", f"{directory}/{filename}.csv")

    # setting parameters

    dgc.set_trig(trigRate)
    timedelay = acqs / trigRate

    print(
        f"At a trigger rate of {trigRate} with {acqs} acquisitions, each run the oscilloscope will require a time delay of {timedelay}"
    )

    iterations = abs(StopFreqinput - totalFreq) / stepsize
    totalTime = (
        iterations * timedelay + 14 * iterations
    ) / 60  # in minutes includes zaber scanning time

    print(f"The estimated time for this scan is at least {totalTime} mins")

    valonFreq = totalFreq - awgFreq
    valon.write_cmd(f"Frequency {valonFreq} MHz")
    StopFreq = StopFreqinput - awgFreq

    try:
        StepSize = float(stepsize)
        stepUpVar = True
        valon.write_cmd(f"FrequencyStep {StepSize} MHz")
    except ValueError:
        stepUpVar = False
        print("Only running single sequence.")
    try:
        StopFreq = float(StopFreq)
        StopFreqVar = True
    except ValueError:
        StopFreqVar = False
        print("No end frequency set. ")

    print("All parameters set, moving to run sequence.")


def CalibrateAndRun():
    global maxList, timeList, endPosZaber, NewFreq, TotalFrequency, startPosZaber
    maxList = []
    timeList = []
    maxMaxVals = []
    runBool = True
    NewFreq = valonFreq

    ### First Run ###
    # status = MyPTE1.Set_Switch("A", 0)
    currPos = zaber.get_pos()
    print("Zaber is at position", currPos)
    oscilloscope.set_settings(channel, gatepos)
    # oscilloscope.recallsetup(setup)
    # run experiment
    getWave()

    dgc.start_pulse()
    dgc.set_trig(trigRate)

    # collect data
    xxValues, yyValues = fftFromScope()

    # stop scope and pulse valve
    oscilloscope.calib_stop()
    dgc.stop_pulse()

    (
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
    ) = oscilloscope.grab_param()

    Parameters = [
        trigRate,
        acqs,
        timeScale,
        timeStart,
        verticalScale,
        verticalOffset,
        verticalPosition,
        Resolution,
        GatePos,
        GateWidth,
    ]

    ParameterLabel = [
        "Trigger Rate",
        "acquisitions",
        "Horizontal Spacing",
        "Time Start",
        "Vertical Scale",
        "Vertical Offset",
        "Vertical Position",
        "Resolution",
        "Gate Position",
        "Gate Width",
    ]

    # For exporting
    TotalFrequency = NewFreq + awgFreq
    UpperBound = TotalFrequency + StepSize / 2
    LowerBound = TotalFrequency - StepSize / 2

    print(UpperBound)
    print(LowerBound)

    DF1 = pd.DataFrame({"Frequency (MHz)": xxValues, "Intensity": yyValues})
    DF2 = pd.DataFrame(
        {
            "Center Freq": [TotalFrequency],
            "Cavity Position": [currPos],
            "Intensity of Cavity": [Intensity],
        }
    )

    DF1_2 = DF1.loc[
        ((DF1["Frequency (MHz)"] >= LowerBound) & (DF1["Frequency (MHz)"] <= UpperBound))
    ]

    if StepDirection == "down":
        DF1_2 = DF1_2[::-1]

    DF3 = pd.DataFrame({"Scope Parameter": ParameterLabel, "Value": Parameters})
    DF1 = DF1.reset_index()
    DF1_2 = DF1_2.reset_index()
    DF2 = DF2.reset_index()

    pd.concat([pd.concat([DF1, DF2], axis=1)]).to_csv(
        f"{rundirectory}/{TotalFrequency}.csv", mode="w+", index=False
    )  # Individual full data
    pd.concat([pd.concat([DF1_2, DF2, DF3], axis=1)]).to_csv(
        f"{directory}/{filename}.csv", mode="a", index=False
    )  # appended main file with filtered data

    if stepUpVar == True and StopFreqVar == True and StepDirection == "up" and NewFreq < StopFreq:
        valon.step_up()
    elif (
        stepUpVar == True
        and StopFreqVar == True
        and StepDirection == "down"
        and NewFreq >= StopFreq
    ):
        valon.step_down()
    else:
        raise ValueError("ERROR: Valon didn't step in first run.")

    ### All Other Runs ###
    i = 1
    while runBool:
        maxList = []
        timeList = []
        maxMaxVals = []

        currPos = zaber.get_pos()

        oscilloscope.set_tuning_settings(channel)
        time.sleep(10)  # TODO: Figure out how to remove this
        oscilloscope.calib_stop()

        if StepDirection == "up":
            NewFreq = valonFreq + StepSize * i
            startPosZaber = currPos - 0.01
            endPosZaber = currPos + 0.06
        elif StepDirection == "down":
            NewFreq = valonFreq - StepSize * i
            startPosZaber = currPos + 0.01
            endPosZaber = currPos - 0.06

        TotalFrequency = NewFreq + awgFreq
        print(f"the new center freq is: {TotalFrequency}")
        print(f"The new Valon Frequency is: {NewFreq}")
        currPos = zaber.get_pos()

        print(
            "Attempting to travel from ",
            startPosZaber,
            " mm to ",
            endPosZaber,
            " mm",
        )

        # TODO: Refactor to be verified at the top
        if endPosZaber <= 50 and startPosZaber <= 50 and endPosZaber >= 0 and startPosZaber >= 0:
            runBool = True
        elif endPosZaber > 50 and startPosZaber <= 50 and endPosZaber >= 0 and startPosZaber >= 0:
            runBool = False
            print("The end of the zaber extension has been reached, this will be the last run.")
        elif endPosZaber < 0 and startPosZaber < 50:
            runBool = False
            print("The zaber has reached home, this will be the last run.")
        elif endPosZaber < 0 or startPosZaber < 0 or startPosZaber > 50:
            raise ValueError("Invalid integers somewhere. The numbers must be between 0 and 50mm.")

        # Retuning of the cavity position
        cavity.retune_cavity_position(startPosZaber, speedZaber)
        dgc.start_trig()

        # setting up threading for scanning
        threadZaber1 = threading.Thread(target=zaberThread)
        threadAcquire1 = threading.Thread(target=acquireThread)

        threads1 = [threadZaber1, threadAcquire1]

        for threadInstances in threads1:
            threadInstances.start()
        for threadInstances in threads1:
            threadInstances.join()

        oscilloscope.calib_stop()

        print("aq length: ", len(maxList))

        # processing scanned information and plotting it
        for maxLists in maxList:
            posArr1 = np.linspace(startPosZaber, endPosZaber, len(maxLists))
            print("Length of max: ", len(maxList))
            print("Length of pos: ", len(posArr1))
            maxIntensity = max(maxLists)
            print(max(maxLists))

            # Plot position vs intensity
            plotter.plot_position_vs_intensity(posArr1, maxLists)

        for items in maxList:
            print("len: ", len(items))
            maxer = max(items)
            for index, values in enumerate(items):
                if values == maxer:
                    print("Max position found: ", posArr1[index])
                    peakMax = posArr1[index]
                    maxMaxVals.append(peakMax)

        peakMidpt1 = round(len(maxMaxVals) / 2)
        max_pos = maxMaxVals[peakMidpt1]
        plt.close()

        # moving to new cavity position for next data acquisition
        cavity.move_cavity_position(max_pos)

        dgc.set_trig(trigRate)

        oscilloscope.set_settings(channel, gatepos)
        getWave()
        dgc.start_pulse()
        xxValues1, yyValues1 = fftFromScope()
        oscilloscope.calib_stop()
        dgc.stop_pulse()

        # filtering exported data to bandwidth of the cavity ## this equation only works when stepsize is at max the width of the cavity bandwidth
        UpperBound = TotalFrequency + StepSize / 2
        LowerBound = TotalFrequency - StepSize / 2

        # Individual file
        DF1 = pd.DataFrame({"Frequency (MHz)": xxValues1, "Intensity": yyValues1})
        DF3 = pd.DataFrame({"Zaber Position(mm):": posArr1, "Intensity": maxLists})
        DF2 = pd.DataFrame(
            {
                "Center Freq": [TotalFrequency],
                "Cavity Position": [currPos / 20997],
                "Intensity of Cavity": [maxIntensity],
            }
        )
        DF1_2 = DF1.loc[
            ((DF1["Frequency (MHz)"] >= LowerBound) & (DF1["Frequency (MHz)"] <= UpperBound))
        ]
        if StepDirection == "down":
            DF1_2 = DF1_2[::-1]

        DF1 = DF1.reset_index()
        DF3 = DF3.reset_index()
        DF1_2 = DF1_2.reset_index()
        DF2 = DF2.reset_index()

        j = 0
        pd.concat([pd.concat([DF1, DF3, DF2], axis=1)]).to_csv(
            f"{rundirectory}/{TotalFrequency}.csv", mode="w+", index=False
        )
        pd.concat([pd.concat([DF1_2, DF2], axis=1)]).to_csv(
            f"{directory}/{filename}.csv", mode="a", index=False, header=False
        )

        print("run #", i + 1, "has been added to: ", f"{directory}/{filename}.csv")

        ### determining if there will be subsequent runs
        if not runBool:
            zaber.home()
            dgc.stop_trig()
            print(f"The experiment has ended. Your data can be found in {directory}/{filename}.csv")
            break

        if (
            stepUpVar == True
            and StopFreqVar == True
            and StepDirection == "up"
            and NewFreq < StopFreq
        ):
            i += 1
            valon.step_up()
        elif (
            stepUpVar == True
            and StopFreqVar == True
            and StepDirection == "down"
            and NewFreq >= StopFreq
        ):
            i += 1
            valon.step_down()
        elif NewFreq > StopFreq and StepDirection == "up":
            runBool = False
            zaber.home()
            dgc.stop_trig()
            print(
                "You have reached the stop frequency. You will find your data in .csv file: ",
                f"{directory}/{filename}.csv",
            )
            break
        elif NewFreq < StopFreq and StepDirection == "down":
            zaber.home()
            dgc.stop_trig()
            print(
                "You have reached the stop frequency. You will find your data in .csv file: ",
                f"{directory}/{filename}.csv",
            )
            break


def zaberThread():
    global loopVar
    loopVar = True
    timeZaberStart = time.perf_counter()
    zaber.move_to(endPosZaber)
    timeZaberEnd = time.perf_counter()
    currPos = zaber.get_pos()
    print("Zaber is at end position: ", currPos, " mm")
    totalTimeZaber = timeZaberEnd - timeZaberStart
    print("Zaber move time (s): ", totalTimeZaber)
    loopVar = False
    timeList.append(totalTimeZaber)
    return


# vcurrently doesn't run based on trigFreq, if required then use if/else with time.perfcounter()
def acquireThread():
    global loopVar
    tempMaxList = []
    while loopVar:
        # currently we are not acquiring based on frequency
        tempMaxList.append(float(oscilloscope.query_cmd("MEASUrement:MEAS1:VALUE?")))

    maxList.append(tempMaxList)


def fftFromScope():
    global timeScale, timeStart, verticalScale, verticalOffset, verticalPosition, FreqCent, FreqSpan

    waveValues = oscilloscope.acq_ft_curve(channel, timedelay)

    (
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
    ) = oscilloscope.grab_param()
    Start = FreqCent - FreqSpan / 2
    # acquire vals
    xValues, yValues = scaleFFT(waveValues, Start)

    plotter.generate_plot(xValues, yValues)

    return xValues, yValues


def getWave():
    getWave = oscilloscope.acquire_fft_data_at_max()
    return getWave


def scaleFFT(waveValues, Start):

    fftYValues = np.array(waveValues, dtype="float")
    fftXValues = (
        np.linspace(timeStart, timeScale * len(waveValues), len(waveValues), endpoint=False)
        / 1000000
    )
    Start = Start / 1000000
    fftXValues = [x + NewFreq for x in fftXValues]
    fftXValues = [x + Start for x in fftXValues]
    newfftXValues = fftXValues[3:]
    newfftYValues = fftYValues[3:]
    return newfftXValues, newfftYValues


def main():
    # Input Validation
    # TODO: Move this to gui
    if StepDirection not in ["up", "down"]:
        raise ValueError(f"{StepDirection} is an invalid StepDirection")

    if speedZaber <= 0 or speedZaber > 2:
        raise ValueError(f"Speedzaber is set to invalid speed: {speedZaber}")

    if totalFreq < StopFreqinput and StepDirection == "down":
        raise ValueError("Stopfreq more that toalfreq and moving down.")
    elif totalFreq > StopFreqinput and StepDirection == "up":
        raise ValueError("Stopfreq less that toalfreq and moving up.")

    initializeInstruments()
    setParameters()
    CalibrateAndRun()


if __name__ == "__main__":
    main()
