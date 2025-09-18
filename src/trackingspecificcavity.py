import zaberController, oscilloscopeController, valonController, SRScontroller
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
import time
import os


# first need to verify there is a cavity where it is centered


def initializeInstruments():
    global valonConnect
    try:
        oscilloscopeController.initializeScope()
        SRScontroller.initializeSRS()
        valonConnect = valonController.initializeValon("COM3")
        valonController.valonSettings(RFLevel=13)
        zaberController.initializeZaber()
    except PermissionError:
        print("ATTN: Permission Error. Make sure Valon and Zaber windows are closed.")


def SetParam():
    global valonFreq, StepSize
    # Setting Frequencies
    awgFreq = 30
    totFreq = float(input("what is your starting frequency (include awg freq) MHz: "))
    valonFreq = totFreq - awgFreq
    StepSize = float(input("What step frequency do you want (MHz)?: "))
    valonController.writeValonCommand(f"Frequency {valonFreq} MHz")
    valonController.writeValonCommand(f"FrequencyStep {StepSize} MHz")


def CavityTrack():
    global maxList, timeList, posArr, maxIntensity, endPosZaber, startPosZaber, speedZaber, speedZaber1
    maxList = []
    timeList = []
    maxMaxVals = []
    oscilloscopeController.recallsetupScopeCavity()
    runBool = "y"
    i = 0
    k = 0
    folderpath = "TrackSingleCavity"
    filename = input("What name to add to file?: ")

    # creating directory
    if not os.path.exists(f"{folderpath}"):
        os.makedirs(f"{folderpath}")
        print("folder for data has been created: ", f"{folderpath}")

    directory = f"{folderpath}/{filename}_{k}"
    if not os.path.exists(f"{directory}.csv"):
        open(f"{directory}.csv", "w+")
        print("Sucessfully named file ", f"{directory}.csv")

    # Setting Frequencies

    while runBool == "y":
        maxList = []
        timeList = []
        maxMaxVals = []

        currPos = zaberController.zaberDevice.get_position()
        currPosMM = currPos / 20997.375
        print("Zaber is starting at position", currPosMM)

        # valonController.writeValonCommand(f'Frequency {valonFreq} MHz')
        startPosZaber = currPosMM + 0.05  # change sign depending on which direction
        endPosZaber = startPosZaber - 0.2

        # for plotting
        startPosZaberMM = startPosZaber
        endPosZaberMM = endPosZaber

        if (
            endPosZaber <= 50
            and startPosZaber <= 50
            and endPosZaber >= 0
            and startPosZaber >= 0
        ):
            endPosZaber = round(endPosZaber * 20997.375)
            startPosZaber = round(startPosZaber * 20997.375)
            runBool = "y"
        elif (
            endPosZaber > 50
            and startPosZaber <= 50
            and endPosZaber >= 0
            and startPosZaber >= 0
        ):
            endPosZaber = 50
            endPosZaber = round(endPosZaber * 20997.375)
            startPosZaber = round(startPosZaber * 20997.375)
            runBool = "n"
            print("This is your last scan, you are at 40 mm.")
        elif endPosZaber < 0 and startPosZaber > 0 and startPosZaber <= 50:
            endPosZaber = 0
            endPosZaber = round(endPosZaber * 20997.375)
            runBool = "n"
            print("This is your last scan, you are at 0 mm.")

        elif startPosZaber < 0 or startPosZaber > 50:
            print("Integer error somewhere or at 50 mm.")
            break

        speedZaber = 0.01
        speedZaber1 = round(speedZaber * 34402.099737532773)

        SRScontroller.setFreq(400)

        zaberController.zaberSetSpeed(
            101204
        )  # speed for moving to the beginning spot not the speed

        print(f"Moving Zaber to {startPosZaberMM}")
        zaberController.moveToZaber(startPosZaber)
        zaberController.zaberDevice.poll_until_idle()
        zaberController.zaberSetSpeed(speedZaber1)
        time.sleep(2)
        oscilloscopeController.oscCalibStart()
        SRScontroller.startTrig()

        threadZaber = threading.Thread(target=zaberThread)
        threadAcquire = threading.Thread(target=acquireThread)

        threads = [threadZaber, threadAcquire]

        for threadInstances in threads:
            threadInstances.start()
        for threadInstances in threads:
            threadInstances.join()

        oscilloscopeController.oscCalibStop()

        print("aq length: ", len(maxList))

        for maxLists in maxList:
            posArr = np.linspace(startPosZaberMM, endPosZaberMM, len(maxLists))
            print("Length of max: ", len(maxList))
            print("Length of pos: ", len(posArr))
            maxIntensity = max(maxLists)
            print(max(maxLists))
            plt.plot(posArr, maxLists)
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
                    print("Max position found: ", posArr[index])
                    peakMax = posArr[index]
                    maxMaxVals.append(peakMax)

        peakMidpt1 = round(len(maxMaxVals) / 2)
        maxPos = maxMaxVals[peakMidpt1]
        plt.close()
        print("Moving to maximum position at: ", maxPos, " mm")
        zaberController.zaberSetSpeed(101204)
        zaberController.moveToZaber(int(maxPos * 20997))
        zaberController.zaberDevice.poll_until_idle()
        currPos = zaberController.zaberDevice.get_position()
        print("Running scan... Zaber is at position: ", currPos / 20997)
        placeholder = valonFreq - i  # change signs depending on which direction

        DF1 = pd.DataFrame(
            {
                "Center Frequency": placeholder,
                "Cavity Position (mm):": [maxPos],
                "Intensity (V)": [maxIntensity],
            }
        )
        if i == 0:
            DF1.to_csv(f"{directory}.csv", mode="a", index=False)
        else:
            DF1.to_csv(f"{directory}.csv", mode="a", index=False, header=False)

        if runBool == "y":
            i += 1
            # valonController.valonStepUp()
            valonController.valonStepDown()

        if runBool == "n":
            print(
                f"Experiment concluded. You will find your data in .csv file: ",
                f"{directory}.csv",
            )


def zaberThread():
    global loopVar
    loopVar = 1
    timeZaberStart = time.perf_counter()
    zaberController.zaberStart((speedZaber1))
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


def acquireThread():
    global loopVar
    tempMaxList = []
    while loopVar == 1:
        # currently we are not acquiring based on frequency
        tempMaxList.append(
            float(oscilloscopeController.queryOscCmd("MEASUrement:MEAS1:VALUE?"))
        )

    maxList.append(tempMaxList)


def main():
    initializeInstruments()
    SetParam()
    CavityTrack()


if __name__ == "__main__":
    main()
