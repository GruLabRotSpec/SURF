import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
import os
from scipy.signal import find_peaks

from enum import Enum

import plot as plotter
from delay_generator_controller import DelayGeneratorController
from zaber_controller import ZaberController
from oscilloscope_controller import OscilloscopeController
from valon_controller import ValonController
from switch_controller import SwitchController
from awg_controller import AWGController
from Cavity import Cavity  # Remove this class later


class StepDirection(Enum):
    Down = -1
    Up = 1


class Spectrometer:
    def __init__(self):
        self.__status = "Idle"

        # Instrument settings (infrequently changed)
        self.__zaber_speed = 0.01  # In mm/s
        self.__zaber_homing_speed = 2.0
        self.__oscilloscope_channel = "CH4"
        self.__rf_level = 10

        # Experiment settings (infrequently changed)
        self.__trig_rate = 5
        self.__acq_rate = 300
        self.__gate_pos = "18.45E-6"
        self.__intensity = 0.2  # Intensity of starting cavity position (V)
        self.__awg_freq = 30  # Frequency for the arbitrary waveform generator

        # Output options
        self.__directory = ""
        self.__run_directory = ""
        self.__folder_name = "Cavity Data"
        self.__filename = "OCS_isotopescan_11700_11200_9_8_25"

        self.__delay_generator_controller = DelayGeneratorController()
        self.__zaber_controller = ZaberController(self.__zaber_speed)
        self.__oscilloscope_controller = OscilloscopeController()
        self.__valon_controller = ValonController("COM3")
        self.__switch_controller = SwitchController()
        self.__awg_controller = AWGController()
        self.__cavity = Cavity(
            self.__zaber_controller,
            self.__oscilloscope_controller,
            self.__delay_generator_controller,
        )

    def get_status(self):
        return self.__status

    def __set_status(self, status):
        self.__status = status

    def scan_frequency(self, start_freq, stop_freq, step_size=0.5):
        if start_freq < stop_freq:
            step_direction = StepDirection.Up
        elif start_freq > stop_freq:
            step_direction = StepDirection.Down
        else:
            return

        # Toggle switch
        self.__switch_controller.set_switch_freq()

        # From old function setParameters(self):
        global valon_freq, step_up_var, stop_freq_var, time_delay
        stop_freq_input = stop_freq

        # Creating directory for output files
        k = 0

        if not os.path.exists(f"{self.__folder_name}/{self.__filename}_{k}"):
            os.makedirs(f"{self.__folder_name}/{self.__filename}_{k}")
            os.makedirs(f"{self.__folder_name}/{self.__filename}_{k}/CavityFiles")
            print(
                "folder for data has been created: ",
                f"{self.__folder_name}/{self.__filename}_{k}",
            )
        else:
            while os.path.exists(f"{self.__folder_name}/{self.__filename}_{k}"):
                k += 1
            os.makedirs(f"{self.__folder_name}/{self.__filename}_{k}")
            os.makedirs(f"{self.__folder_name}/{self.__filename}_{k}/CavityFiles")
            print(
                "folder for data has been created: ",
                f"{self.__folder_name}/{self.__filename}_{k}",
            )

        self.__directory = f"{self.__folder_name}/{self.__filename}_{k}"
        self.__run_directory = f"{self.__folder_name}/{self.__filename}_{k}/CavityFiles"

        if not os.path.exists(f"{self.__directory}/{self.__filename}.csv"):
            open(f"{self.__directory}/{self.__filename}.csv", "w+")
            print(
                "Successfully named file ", f"{self.__directory}/{self.__filename}.csv"
            )

        # setting parameters

        self.__delay_generator_controller.set_trig(self.__trig_rate)
        time_delay = self.__acq_rate / self.__trig_rate

        print(
            f"At a trigger rate of {self.__trig_rate} with {self.__acq_rate} acquisitions, each run the oscilloscope will require a time delay of {time_delay}"
        )

        iterations = abs(stop_freq_input - start_freq) / step_size
        total_time = (
            iterations * time_delay + 14 * iterations
        ) / 60  # Includes zaber scanning time (in minutes)

        print(f"The estimated time for this scan is at least {total_time} mins")

        valon_freq = start_freq - self.__awg_freq
        self.__valon_controller.write_cmd(f"Frequency {valon_freq} MHz")
        self.__valon_controller.write_cmd(f"FrequencyStep {step_size} MHz")

        stop_freq = stop_freq_input - self.__awg_freq
        step_size = float(step_size)

        print("All parameters set, moving to run sequence.")

        # From old function CalibrateAndRun
        # TotalFrequency does not appear to be the same as self.__total_freq
        global max_list, time_list, new_freq, total_frequency

        max_list = []
        time_list = []
        max_max_vals = []
        run_bool = True
        new_freq = valon_freq

        ### First Run ###
        curr_pos = self.__zaber_controller.get_pos()
        print("Zaber is at position", curr_pos)

        self.__oscilloscope_controller.set_settings(
            self.__oscilloscope_channel, self.__gate_pos
        )
        self.__get_wave()

        self.__delay_generator_controller.start_pulse()
        self.__delay_generator_controller.set_trig(self.__trig_rate)

        # collect data
        xx_values, yy_values = self.__fft_from_scope(new_freq)

        # stop scope and pulse valve
        self.__oscilloscope_controller.calib_stop()
        self.__delay_generator_controller.stop_pulse()

        # For exporting
        total_frequency = new_freq + self.__awg_freq
        upper_bound = total_frequency + step_size / 2
        lower_bound = total_frequency - step_size / 2

        print(upper_bound)
        print(lower_bound)

        self.write_data_to_csv(
            xx_values, yy_values, lower_bound, upper_bound, curr_pos, step_direction
        )

        if step_direction == StepDirection.Up and new_freq < stop_freq:
            self.__valon_controller.step_up()
        elif step_direction == StepDirection.Down and new_freq >= stop_freq:
            self.__valon_controller.step_down()
        else:
            raise ValueError("ERROR: Valon didn't step in first run.")

        ### All Other Runs ###
        run_number = 1
        while run_bool:
            max_list = []
            time_list = []
            max_max_vals = []

            curr_pos = self.__zaber_controller.get_pos()

            self.__oscilloscope_controller.set_tuning_settings(
                self.__oscilloscope_channel
            )
            time.sleep(10)  # TODO: Figure out how to remove this
            self.__oscilloscope_controller.calib_stop()

            if step_direction == StepDirection.Up:
                new_freq = valon_freq + step_size * run_number
                start_pos_zaber = curr_pos - 0.01
                end_pos_zaber = curr_pos + 0.03
            elif step_direction == StepDirection.Down:
                new_freq = valon_freq - step_size * run_number
                start_pos_zaber = curr_pos
                end_pos_zaber = curr_pos - 0.06
            else:
                raise ValueError("Invalid step direction", step_direction)

            total_frequency = new_freq + self.__awg_freq
            print(f"the new center freq is: {total_frequency}")
            print(f"The new Valon Frequency is: {new_freq}")
            curr_pos = self.__zaber_controller.get_pos()

            print(
                "Attempting to travel from ",
                start_pos_zaber,
                " mm to ",
                end_pos_zaber,
                " mm",
            )

            # Retuning of the cavity position
            self.__cavity.retune_cavity_position(start_pos_zaber, self.__zaber_speed)
            self.__delay_generator_controller.start_trig()

            # setting up threading for scanning
            thread_zaber_1 = threading.Thread(
                target=self.__zaber_thread, args=[end_pos_zaber]
            )
            thread_acquire_1 = threading.Thread(target=self.__acquire_thread)

            threads1 = [thread_zaber_1, thread_acquire_1]

            for thread_instances in threads1:
                thread_instances.start()
            for thread_instances in threads1:
                thread_instances.join()

            self.__oscilloscope_controller.calib_stop()

            print("aq length: ", len(max_list))

            # processing scanned information and plotting it
            for max_lists in max_list:
                posArr1 = np.linspace(start_pos_zaber, end_pos_zaber, len(max_lists))
                print("Length of max: ", len(max_list))
                print("Length of pos: ", len(posArr1))
                max_intensity = max(max_lists)
                print(max(max_lists))

                # Plot position vs intensity
                # plotter.plot_position_vs_intensity(posArr1, max_lists)

            for items in max_list:
                print("len: ", len(items))
                maxer = max(items)
                for index, values in enumerate(items):
                    if values == maxer:
                        print("Max position found: ", posArr1[index])
                        peakMax = posArr1[index]
                        max_max_vals.append(peakMax)

            peakMidpt1 = round(len(max_max_vals) / 2)
            max_pos = max_max_vals[peakMidpt1]
            plt.close()

            # moving to new cavity position for next data acquisition
            self.__cavity.move_cavity_position(max_pos)

            self.__delay_generator_controller.set_trig(self.__trig_rate)

            self.__oscilloscope_controller.set_settings(
                self.__oscilloscope_channel, self.__gate_pos
            )
            self.__get_wave()
            self.__delay_generator_controller.start_pulse()
            xx_values_1, yy_values_1 = self.__fft_from_scope(new_freq)
            self.__oscilloscope_controller.calib_stop()
            self.__delay_generator_controller.stop_pulse()

            # filtering exported data to bandwidth of the cavity ## this equation only works when stepsize is at max the width of the cavity bandwidth
            upper_bound = total_frequency + step_size / 2
            lower_bound = total_frequency - step_size / 2

            self.write_data_to_csv(
                xx_values_1,
                yy_values_1,
                lower_bound,
                upper_bound,
                curr_pos,
                step_direction,
            )

            print(
                "run #",
                run_number + 1,
                "has been added to: ",
                f"{self.__directory}/{self.__filename}.csv",
            )

            # Check for stop Freq
            if new_freq > stop_freq and step_direction == StepDirection.Up:
                print("You have reached the stop frequency")
                break
            elif new_freq < stop_freq and step_direction == StepDirection.Down:
                print("You have reached the stop frequency")
                break

            # Check for end of zaber
            if end_pos_zaber > 50 or start_pos_zaber > 50:
                print("The end of the zaber extension has been reached")
                break
            elif end_pos_zaber <= 0 or start_pos_zaber < 0:
                print("The zaber has reached home")
                break

            # Step
            if step_direction == StepDirection.Up:
                self.__valon_controller.step_up()
            elif step_direction == StepDirection.Down:
                self.__valon_controller.step_down()

            run_number += 1

        # Cleanup
        self.__zaber_controller.home()
        self.__delay_generator_controller.stop_trig()
        print(
            f"Run is finished. You will find your data in .csv file: {self.__directory}/{self.__filename}.csv"
        )

    def cavity_search(self, stop_freq, step_size):
        # This code is meant to scan the whole region from 0 - 40 mm and find all the cavity positions for a set frequency
        global valon_freq, step_up_var, stop_freq_var
        stop_freqinput = stop_freq

        valon_freq = stop_freq - self.__awg_freq
        self.__valon_controller.write_cmd(f"Frequency {valon_freq} MHz")

        # Toggle switch
        self.__switch_controller.set_switch_cavity()

        # Set tuning settings
        self.__oscilloscope_controller.set_tuning_settings(self.__oscilloscope_channel)

        k = 0
        self.__folder_name = "Cavity Scan"

        # creating directory for files to be

        if not os.path.exists(f"{self.__folder_name}/{self.__filename}_{k}"):
            os.makedirs(f"{self.__folder_name}/{self.__filename}_{k}")
            os.makedirs(f"{self.__folder_name}/{self.__filename}_{k}/CavityRuns")
            print(
                "folder for data has been created: ",
                f"{self.__folder_name}/{self.__filename}_{k}",
            )
        else:
            while os.path.exists(f"{self.__folder_name}/{self.__filename}_{k}"):
                k += 1
            os.makedirs(f"{self.__folder_name}/{self.__filename}_{k}")
            os.makedirs(f"{self.__folder_name}/{self.__filename}_{k}/CavityRuns")
            print(
                "folder for data has been created: ",
                f"{self.__folder_name}/{self.__filename}_{k}",
            )

        self.__directory = f"{self.__folder_name}/{self.__filename}_{k}"
        self.__run_directory = f"{self.__folder_name}/{self.__filename}_{k}/CavityRuns"

        if not os.path.exists(f"{self.__directory}/{self.__filename}.csv"):
            open(f"{self.__directory}/{self.__filename}.csv", "w+")
            print(
                "Sucessfully named file ", f"{self.__directory}/{self.__filename}.csv"
            )

        self.__zaber_controller.set_speed(self.__zaber_homing_speed)
        self.__zaber_controller.home()

        print("Zaber has arrived at home position 0 mm")
        # stop_freq = stop_freqinput - self.__awg_freq
        try:
            step_size = float(step_size)
            step_up_var = True
            self.__valon_controller.write_cmd(f"FrequencyStep {step_size} MHz")
        except ValueError:
            step_up_var = False
            print("Only running single sequence.")
        try:
            stop_freq = float(stop_freqinput)
            stop_freq_var = True
        except ValueError:
            stop_freq_var = False
            print("No end frequency set. ")

        print("All parameters acquired, moving to calibrate and run sequence.")

        global speed_zaber, max_list, time_list
        max_list = []
        time_list = []
        run_bool = True
        i = 0

        while run_bool:
            new_freq = valon_freq + step_size * i + self.__awg_freq
            print(f"The new Valon Frequency is: {new_freq}")

            start_pos_zaber_mm = 0
            end_pos_zaber_mm = 50

            self.__delay_generator_controller.set_frequency(
                300
            )  # Trigger rate for cavity search
            self.__zaber_controller.set_speed(self.__zaber_homing_speed)
            self.__zaber_controller.home()

            curr_pos = self.__zaber_controller.get_pos()

            print("Zaber is at position ", curr_pos)
            self.__zaber_controller.set_speed(self.__zaber_speed)

            time.sleep(2)
            self.__oscilloscope_controller.calib_start()
            self.__delay_generator_controller.start_trig()

            thread_zaber_1 = threading.Thread(
                target=self.__zaber_thread, args=[end_pos_zaber_mm]
            )
            thread_acquire_1 = threading.Thread(target=self.__acquire_thread)

            threads_1 = [thread_zaber_1, thread_acquire_1]

            for thread_instances in threads_1:
                thread_instances.start()
            for thread_instances in threads_1:
                thread_instances.join()

            self.__delay_generator_controller.stop_trig()
            self.__oscilloscope_controller.calib_stop()

            for max_lists in max_list:
                pos_arr = np.linspace(
                    start_pos_zaber_mm, end_pos_zaber_mm, len(max_lists)
                )
                print("Length of max: ", len(max_lists))
                print("Length of pos: ", len(pos_arr))

                DF = pd.DataFrame(
                    {
                        "Zaber Position (mm)": pos_arr,
                        "Intensity (Volts)": max_lists,
                        "Frequency": new_freq,
                    }
                )
                x = DF["Zaber Position (mm)"]
                y = DF["Intensity (Volts)"]

            # threshold = input('Threshold for peak selection (in V): ')
            threshold = 0.008
            peaks, _ = find_peaks(y, height=threshold)

            # plt.plot(x, y)
            # plt.plot(x[peaks], y[peaks], "x")
            # plt.title("Zaber Position vs. Intensity")
            # plt.xlabel("Zaber Position (mm)")
            # plt.ylabel("Intensity (Volts)")
            # plt.show(block=False)
            # plt.pause(10)
            # plt.close()

            df1 = pd.DataFrame(
                {
                    "Zaber Position (mm)": x,
                    "Intensity (V)": y,
                    "Frequency (MHz)": new_freq,
                }
            )
            df2 = pd.DataFrame({"Peaks": x[peaks], "Intensity": y[peaks]})
            df2 = df2.reset_index(drop=True)
            pd.concat([pd.concat([df1, df2], axis=1)]).to_csv(
                f"{self.__directory}/{self.__filename}.csv", mode="a", index=False
            )
            pd.concat([pd.concat([df1, df2], axis=1)]).to_csv(
                f"{self.__run_directory}/{new_freq}MHz.csv", mode="w+", index=False
            )

            print(
                "run #",
                i + 1,
                "has been added to: ",
                f"{self.__directory}/{self.__filename}.csv",
            )

            self.__delay_generator_controller.stop_trig()
            self.__oscilloscope_controller.calib_stop()

            if step_up_var and stop_freq_var:
                if new_freq < stop_freq:
                    i += 1
                    self.__valon_controller.step_up()

                else:
                    print(
                        "You have reached the stop frequency. You will find your data in .csv file: ",
                        f"{self.__directory}/{self.__filename}.csv",
                    )
                    break

            elif step_up_var and not stop_freq_var:
                run_bool = input(
                    "Do you want to run another experiment? (Y/N): "
                ).lower()
                if run_bool:
                    i += 1
                    self.__valon_controller.step_up()
                if not run_bool:
                    print(
                        "Experiment concluded. You will find your data in .csv file: ",
                        f"{self.__directory}/{self.__filename}.csv",
                    )
                    self.__zaber_controller.home()
                break

    def __zaber_thread(self, end_pos_zaber):
        global loop_var
        loop_var = True
        time_zaber_start = time.perf_counter()

        self.__zaber_controller.move_to(end_pos_zaber)

        time_zaber_end = time.perf_counter()
        curr_pos = self.__zaber_controller.get_pos()

        print("Zaber is at end position: ", curr_pos, " mm")
        total_time_zaber = time_zaber_end - time_zaber_start
        print("Zaber move time (s): ", total_time_zaber)

        loop_var = False
        time_list.append(total_time_zaber)
        return

    # Currently doesn't run based on trigFreq, if required then use if/else with time.perfcounter()
    def __acquire_thread(self):
        global loop_var
        temp_max_list = []
        while loop_var:
            # Currently we are not acquiring based on frequency
            temp_max_list.append(
                float(
                    self.__oscilloscope_controller.query_cmd("MEASUrement:MEAS1:VALUE?")
                )
            )

        max_list.append(temp_max_list)

    def __fft_from_scope(self, new_freq):
        global time_scale, time_start, vertical_scale, vertical_offset, vertical_position, freq_cent, freq_span

        wave_values = self.__oscilloscope_controller.acq_ft_curve(
            self.__oscilloscope_channel, time_delay
        )

        (
            time_scale,
            time_start,
            vertical_scale,
            vertical_offset,
            vertical_position,
            freq_cent,
            freq_span,
            resolution,
            gate_pos,
            gate_width,
        ) = self.__oscilloscope_controller.grab_param()
        start = freq_cent - freq_span / 2
        # acquire vals
        x_values, y_values = self.__scale_fft(wave_values, start, new_freq)

        # plotter.generate_plot(x_values, y_values)

        return x_values, y_values

    def write_data_to_csv(
        self, xx_values, yy_values, lower_bound, upper_bound, curr_pos, step_direction
    ):
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
        ) = self.__oscilloscope_controller.grab_param()

        parameters = [
            self.__trig_rate,
            self.__acq_rate,
            timeScale,
            timeStart,
            verticalScale,
            verticalOffset,
            verticalPosition,
            Resolution,
            GatePos,
            GateWidth,
        ]

        parameter_labels = [
            "Trigger Rate",
            "Acquisitions",
            "Horizontal Spacing",
            "Time Start",
            "Vertical Scale",
            "Vertical Offset",
            "Vertical Position",
            "Resolution",
            "Gate Position",
            "Gate Width",
        ]

        DF1 = pd.DataFrame({"Frequency (MHz)": xx_values, "Intensity": yy_values})
        DF2 = pd.DataFrame(
            {
                "Center Freq": [total_frequency],
                "Cavity Position": [curr_pos],
                "Intensity of Cavity": [self.__intensity],
            }
        )

        DF1_2 = DF1.loc[
            (
                (DF1["Frequency (MHz)"] >= lower_bound)
                & (DF1["Frequency (MHz)"] <= upper_bound)
            )
        ]

        if step_direction == StepDirection.Down:
            DF1_2 = DF1_2[::-1]

        DF3 = pd.DataFrame({"Scope Parameter": parameter_labels, "Value": parameters})

        DF1 = DF1.reset_index()
        DF1_2 = DF1_2.reset_index()
        DF2 = DF2.reset_index()

        pd.concat([pd.concat([DF1, DF2], axis=1)]).to_csv(
            f"{self.__run_directory}/{total_frequency}.csv", mode="w+", index=False
        )  # Individual full data

        pd.concat([pd.concat([DF1_2, DF2, DF3], axis=1)]).to_csv(
            f"{self.__directory}/{self.__filename}.csv", mode="a", index=False
        )  # appended main file with filtered data

    def set_instrument_settings(
        self, zaber_speed=0.003, zaber_homing_speed=2.0, rf_level=10
    ):
        self.__zaber_speed = zaber_speed
        self.__zaber_homing_speed = zaber_homing_speed
        self.__rf_level = rf_level

    def get_instrument_settings(self):
        return (self.__zaber_speed, self.__rf_level)

    def set_experiment_settings(
        self, trig_rate=5, acq_rate=300, gate_pos="18.45E-6", intensity=0.2, awg_freq=30
    ):
        self.__trig_rate = trig_rate
        self.__acq_rate = acq_rate
        self.__gate_pos = gate_pos
        self.__intensity = intensity
        self.__awg_freq = awg_freq

    def get_experiment_settings(self):
        return (
            self.__trig_rate,
            self.__acq_rate,
            self.__gate_pos,
            self.__intensity,
            self.__awg_freq,
        )

    def set_all_options(
        self,
        rf_level,
        zaber_speed,
        zaber_homing_speed,
        awg_status,
        awg_freq,
        awg_run_mode,
        awg_ch_1_output,
        awg_ch_2_output,
        resolution,
        sample_rate,
        window_type,
        gate_pos,
        math_averages,
        trigger_rate,
    ):
        self.set_instrument_settings(zaber_speed, zaber_homing_speed, rf_level)

        # AWG
        if awg_status:
            self.__awg_controller.run()

            if awg_run_mode:
                self.__awg_controller.set_run_mode(awg_run_mode)

            if awg_ch_1_output:
                self.__awg_controller.enable_channel_output(1)
            else:
                self.__awg_controller.disable_channel_output(1)

            if awg_ch_2_output:
                self.__awg_controller.enable_channel_output(2)
            else:
                self.__awg_controller.disable_channel_output(2)

        else:
            self.__awg_controller.stop()

        self.__awg_freq = awg_freq

        # Oscilloscope
        self.__oscilloscope_controller.write_cmd(f"MATH4:SPECTral:RESBw {resolution}")
        self.__oscilloscope_controller.write_cmd(
            f"HORizontal:MODE:SAMPLERate {sample_rate}"
        )
        self.__oscilloscope_controller.write_cmd(f"MATH3:SPECTral:WINdow {window_type}")
        self.__oscilloscope_controller.write_cmd(
            f"MATH4:SPECTral:GATEPOS {gate_position}"
        )
        self.__oscilloscope_controller.write_cmd(f"MATH4:NUMAvg {math_averages}")

        # Delay generator
        self.__delay_generator_controller.set_trig(trig_rate)

    def set_output_options(self, folder_name, filename):
        self.__folder_name = folder_name
        self.__filename = filename

    def get_output_options(self):
        return (self.__folder_name, self.__filename)

    def __get_wave(self):
        get_wave = self.__oscilloscope_controller.acquire_fft_data_at_max()
        return get_wave

    def __scale_fft(self, wave_values, start, new_freq):
        fft_y_values = np.array(wave_values, dtype="float")
        fft_x_values = (
            np.linspace(
                time_start,
                time_scale * len(wave_values),
                len(wave_values),
                endpoint=False,
            )
            / 1000000
        )

        start = start / 1000000
        fft_x_values = [x + new_freq for x in fft_x_values]
        fft_x_values = [x + start for x in fft_x_values]
        new_fft_x_values = fft_x_values[3:]
        new_fft_y_values = fft_y_values[3:]
        return new_fft_x_values, new_fft_y_values
