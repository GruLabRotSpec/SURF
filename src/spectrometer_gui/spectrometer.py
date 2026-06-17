from __future__ import annotations
import math
import time
import tomli_w
import numpy as np
import pandas as pd
import concurrent
import threading
from dataclasses import asdict
from threading import Event
import typing
from scipy.signal import find_peaks

from enum import Enum

from config import Config, save_config
from pathlib import Path
from settings import Settings
from gui.signal_enums import GraphState, ScanType

from delay_generator_controller import DelayGeneratorController
from zaber_controller import ZaberController, ZaberSpeed
from oscilloscope_controller import OscilloscopeController
from valon_controller import ValonController
from switch_controller import SwitchController
from awg_controller import AWGController

import logging
from logger import CustomLogger

if typing.TYPE_CHECKING:
    from frequency_scan_settings import FrequencyScanSettings
    from gui.spectrometer_controller import ScanSignals


class StepDirection(Enum):
    Down = -1
    Up = 1


class Spectrometer:
    def __init__(self, settings: Settings, config: Config):
        # Config
        self.settings = settings
        self.config = config

        # Devices
        self.zaber_controller = ZaberController()
        self.oscilloscope_controller = OscilloscopeController()
        self.valon_controller = ValonController()
        self.switch_controller = SwitchController()
        self.delay_generator_controller = DelayGeneratorController()
        self.awg_controller = AWGController()

        # Logger
        self.logger = CustomLogger("grugui.spectrometer", logging.DEBUG)
        self.logger.logger.debug("This is a logging test.")

        # Output options
        self._directory = ""
        self._run_directory = ""
        self._folder_name = self.settings.output.location
        self._filename = self.settings.output.filename

    def make_dir(self, subdirectory: str) -> str:
        k = 0
        base_path = Path(self._folder_name) / f"{self._filename}_{k}"

        while base_path.exists():
            k += 1
            base_path = Path(self._folder_name) / f"{self._filename}_{k}"

        base_path.mkdir(parents=True)
        (base_path / subdirectory).mkdir(parents=True)
        self.logger.logger.info(f"folder for data has been created: {base_path}")
        return str(base_path)

    def scan_frequency(
        self,
        signals: ScanSignals,
        canceled: Event,
        settings: FrequencyScanSettings,
    ):
        # TODO: Digitizer from the freq scan panel gui
        # are not actually hooked up to anything right now.

        start_freq = settings.scan_parameters.start_freq
        stop_freq = settings.scan_parameters.end_freq
        step_size = settings.scan_parameters.step_size
        start_pos = settings.scan_parameters.zaber_pos

        if start_freq < stop_freq:
            step_direction = StepDirection.Up
        elif start_freq > stop_freq:
            step_direction = StepDirection.Down
        else:
            return

        # Ensure Config is applied
        self.update_config(self.config)

        # Toggle switch
        self.switch_controller.set_switch_freq()

        # Move zaber to start position if specified
        if start_pos is not None:
            self.logger.logger.info(f"Zaber moving to set position: {start_pos}")
            self.zaber_controller.move_to(start_pos, ZaberSpeed.MOVING, True)

        stop_freq_input = stop_freq

        # Creating directory for output files
        self._directory = self.make_dir("CavityFiles")
        self._run_directory = f"{self._directory}/CavityFiles"

        if not Path(f"{self._directory}/{self._filename}.csv").exists():
            header_df = pd.DataFrame(
                columns=[
                    "Frequency (MHz)",
                    "Intensity",
                    "Center Freq",
                    "Cavity Position",
                ]
            )
            header_df.to_csv(f"{self._directory}/{self._filename}.csv", index=False)
            save_config(
                Path(f"{self._directory}/{self._filename}_config.toml"), self.config
            )
            with Path.open(Path(f"{self._directory}/scan_settings.toml"), "wb") as f:
                tomli_w.dump(settings.model_dump(exclude_none=True), f)
            self.logger.logger.info(
                f"Successfully named file {self._directory}/{self._filename}.csv"
            )

        # Custom timing
        self.delay_generator_controller.SPDT_switch(settings.scan_parameters.spdt_width)
        self.delay_generator_controller.gas_MW_delay(settings.scan_parameters.valve_mw_delay)

        self.delay_generator_controller.set_trig()
        self._time_delay = (
            self.oscilloscope_controller.acq_rate
            / self.delay_generator_controller.trigger_rate
        )

        self.logger.logger.info(
            f"At a trigger rate of {self.delay_generator_controller.trigger_rate} with {self.oscilloscope_controller.acq_rate} acquisitions, "
            + f"each run the oscilloscope will require a time delay of {self._time_delay}",
        )

        iterations = math.ceil(abs(stop_freq_input - start_freq) / step_size) + 1
        total_time = (
            iterations * self._time_delay + 14 * iterations
        ) / 60  # Includes zaber scanning time (in minutes)

        self.logger.logger.info(
            f"The estimated time for this scan is at least {total_time} mins, with {iterations} scans"
        )

        valon_freq = start_freq - self.awg_controller.awg_freq
        self.valon_controller.write_cmd(f"Frequency {valon_freq} MHz")
        self.valon_controller.write_cmd(f"FrequencyStep {step_size} MHz")

        stop_freq = stop_freq_input - self.awg_controller.awg_freq
        step_size = float(step_size)

        self.logger.logger.info("All parameters set, moving to run sequence.")

        curr_pos = self.zaber_controller.get_pos()
        self.logger.logger.info(f"Starting scan with zaber at: {curr_pos}")

        ### First Run ###
        self.oscilloscope_controller.set_math4()
        self.oscilloscope_controller.acquire_fft_data_at_max()

        self.delay_generator_controller.start_pulse()
        self.delay_generator_controller.set_trig()

        # collect data
        _, _ = self.fft_from_scope(valon_freq)

        # stop scope and pulse valve
        self.oscilloscope_controller.stop_acq()
        self.delay_generator_controller.stop_pulse()

        ### All Other Runs ###
        run_number = 1
        while True:
            self.oscilloscope_controller.set_math3()
            time.sleep(2)  # TODO: Figure out how to remove this
            self.oscilloscope_controller.stop_acq()

            start_position = self.zaber_controller.get_pos()

            # Step Zaber & Freq
            match step_direction:
                case StepDirection.Up:
                    new_freq = valon_freq + step_size * run_number
                    end_position = start_position + self.zaber_controller.step_size
                case StepDirection.Down:
                    new_freq = valon_freq - step_size * run_number
                    end_position = start_position - self.zaber_controller.step_size

            # Check for end of zaber
            if end_position > 50 or start_position > 50:
                self.logger.logger.info(
                    "The end of the zaber extension has been reached"
                )
                break
            elif end_position < 0 or start_position < 0:
                self.logger.logger.info("The zaber has reached home")
                break

            if canceled.is_set():
                self.logger.logger.info("Scan Canceled")
                break

            total_frequency = new_freq + self.awg_controller.awg_freq
            self.logger.logger.info(f"the new center freq is: {total_frequency}")
            self.logger.logger.info(f"The new Valon Frequency is: {new_freq}")

            signals.progress.emit(
                run_number / iterations,
                f"{run_number} / {iterations} - Freq {new_freq} MHz",
            )

            self.logger.logger.info(
                f"Zaber Scan from {start_position} mm to {end_position} mm"
            )

            # Retuning of the cavity position
            self.delay_generator_controller.set_frequency(300)

            self.delay_generator_controller.start_trig()

            max_list = self.scan_with_acquisition(end_position)

            # TODO: Check if we can just grab the actual positions from the zaber
            pos_array = np.linspace(start_position, end_position, len(max_list))
            peak_idx = np.argmax(max_list)
            max_pos = pos_array[peak_idx]

            self.logger.logger.info(f"Moving to maximum position at: {max_pos} mm")
            self.zaber_controller.move_to(max_pos, ZaberSpeed.MOVING)

            self.delay_generator_controller.set_trig()

            self.oscilloscope_controller.set_math4()
            self.oscilloscope_controller.acquire_fft_data_at_max()

            self.delay_generator_controller.start_pulse()
            frequency_values, intensity_values = self.fft_from_scope(new_freq)
            self.delay_generator_controller.stop_pulse()

            _, filtered_spectrum = self.process_frequency_data(
                total_frequency,
                step_size,
                frequency_values,
                intensity_values,
                max_pos,
                step_direction,
            )

            signals.update_graph.emit(
                GraphState(
                    ScanType.FREQUENCY,
                    pos_array.tolist(),
                    max_list,
                    new_freq,
                    filtered_spectrum["Frequency (MHz)"].to_list(),
                    filtered_spectrum["Intensity"].to_list(),
                )
            )

            self.logger.logger.info(
                f"run #{run_number} has been added to: {self._directory}/{self._filename}.csv",
            )

            # Check for stop Freq
            match step_direction:
                case StepDirection.Up:
                    if new_freq > stop_freq:
                        self.logger.logger.info("You have reached the stop frequency")
                        break
                case StepDirection.Down:
                    if new_freq < stop_freq:
                        self.logger.logger.info("You have reached the stop frequency")
                        break

            # Step
            match step_direction:
                case StepDirection.Up:
                    self.valon_controller.step_up()
                case StepDirection.Down:
                    self.valon_controller.step_down()

            run_number += 1

        # Cleanup
        self.cleanup()
        self.finalize_csv()
        self.logger.logger.info("Run is finished")

    def cavity_search(self, stop_freq, step_size):
        # This code is meant to scan the whole region from 0 - 40 mm and find all the cavity positions for a set frequency
        stop_freqinput = stop_freq

        valon_freq = stop_freq - self.awg_controller.awg_freq
        self.valon_controller.write_cmd(f"Frequency {valon_freq} MHz")

        # Toggle switch
        self.switch_controller.set_switch_cavity()

        # Set tuning settings
        self.oscilloscope_controller.set_math3()

        self._directory = ""
        self._folder_name = "Cavity Scan"

        # creating directory for files to be
        self._directory = self.make_dir("CavityRuns")
        self._run_directory = f"{self._directory}/CavityRuns"

        if not Path(f"{self._directory}/{self._filename}.csv").exists():
            Path(f"{self._directory}/{self._filename}.csv").touch()
            self.logger.logger.info(
                f"Successfully named file {self._directory}/{self._filename}.csv"
            )

        self.zaber_controller.home()

        self.logger.logger.info("Zaber has arrived at home position 0 mm")
        # stop_freq = stop_freqinput - self.__awg_freq
        try:
            step_size = float(step_size)
            step_up_var = True
            self.valon_controller.write_cmd(f"FrequencyStep {step_size} MHz")
        except ValueError:
            step_up_var = False
            self.logger.logger.info("Only running single sequence.")
        try:
            stop_freq = float(stop_freqinput)
            stop_freq_var = True
        except ValueError:
            stop_freq_var = False
            self.logger.logger.info("No end frequency set. ")

        self.logger.logger.info(
            "All parameters acquired, moving to calibrate and run sequence."
        )

        max_list = []
        run_bool = True
        i = 0

        while run_bool:
            new_freq = valon_freq + step_size * i + self.awg_controller.awg_freq
            self.logger.logger.info(f"The new Valon Frequency is: {new_freq}")

            start_pos_zaber_mm = 0
            end_pos_zaber_mm = 50

            self.delay_generator_controller.set_frequency(
                300
            )  # Trigger rate for cavity search
            self.zaber_controller.home()

            curr_pos = self.zaber_controller.get_pos()

            self.logger.logger.info(f"Zaber is at position {curr_pos}")

            self.delay_generator_controller.start_trig()
            max_list.append(self.scan_with_acquisition(end_pos_zaber_mm))
            self.delay_generator_controller.stop_trig()

            for max_lists in max_list:
                pos_arr = np.linspace(
                    start_pos_zaber_mm, end_pos_zaber_mm, len(max_lists)
                )
                self.logger.logger.info(f"Length of max: {len(max_lists)}")
                self.logger.logger.info(f"Length of pos: {len(pos_arr)}")

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
                f"{self._directory}/{self._filename}.csv", mode="a", index=False
            )
            pd.concat([pd.concat([df1, df2], axis=1)]).to_csv(
                f"{self._run_directory}/{new_freq}MHz.csv", mode="w+", index=False
            )

            self.logger.logger.info(
                f"run #{i + 1} has been added to: {self._directory}/{self._filename}.csv",
            )

            self.delay_generator_controller.stop_trig()
            self.oscilloscope_controller.stop_acq()

            if step_up_var and stop_freq_var and new_freq < stop_freq:
                i += 1
                self.valon_controller.step_up()

        self.cleanup()

        self.logger.logger.info(
            f"Experiment concluded. You will find your data in .csv file: {self._directory}/{self._filename}.csv",
        )

    def cleanup(self):
        self.delay_generator_controller.stop_trig()
        self.oscilloscope_controller.stop_acq()
        self.zaber_controller.home()

    def scan_with_acquisition(self, end_pos):
        self.oscilloscope_controller.start_acq()

        # I don't like this, but axis.is_busy() is too slow
        # and I can't find anything better

        # Maybe try fastframe?
        def _gather_data(stop_event):
            data = []
            while not stop_event.is_set():
                data.append(
                    float(
                        self.oscilloscope_controller.query_cmd(
                            "MEASUrement:MEAS1:VALUE?"
                        )
                    )
                )
            return data

        stop_event = threading.Event()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(_gather_data, stop_event)
            self.zaber_controller.move_to(end_pos, ZaberSpeed.SCANNING, blocking=True)
            stop_event.set()

        self.oscilloscope_controller.stop_acq()

        curr_pos = self.zaber_controller.get_pos()
        self.logger.logger.info(f"Zaber moved to: {curr_pos} mm")

        return future.result()

    def fft_from_scope(self, new_freq):
        wave_values = self.oscilloscope_controller.acq_ft_curve(self._time_delay)

        (
            time_scale,
            time_start,
            freq_cent,
            freq_span,
        ) = self.oscilloscope_controller.grab_fft_params()

        start = freq_cent - freq_span / 2 / 1000000

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

        fft_x_values = [x + new_freq for x in fft_x_values]
        fft_x_values = [x + start for x in fft_x_values]

        x_values = fft_x_values[3:]
        y_values = fft_y_values[3:]

        return x_values, y_values

    def process_frequency_data(
        self,
        total_frequency,
        step_size,
        frequency_values,
        intensity_values,
        current_position,
        step_direction,
    ):
        # filtering exported data to bandwidth of the cavity
        upper_bound = total_frequency + step_size / 2
        lower_bound = total_frequency - step_size / 2

        spectrum_data = pd.DataFrame(
            {"Frequency (MHz)": frequency_values, "Intensity": intensity_values}
        )

        metadata = pd.DataFrame(
            {
                "Center Freq": [total_frequency],
                "Cavity Position": [current_position],
            }
        )

        filtered_spectrum = spectrum_data.loc[
            (spectrum_data["Frequency (MHz)"] >= lower_bound)
            & (spectrum_data["Frequency (MHz)"] <= upper_bound)
        ]

        match step_direction:
            case StepDirection.Down:
                filtered_spectrum = filtered_spectrum.iloc[::-1]
            case StepDirection.Up:
                pass

        filtered_spectrum = filtered_spectrum.reset_index(drop=True)

        pd.concat([spectrum_data, metadata], axis=1).to_csv(
            f"{self._run_directory}/{total_frequency}.csv",
            mode="w+",
            index=False,
        )

        pd.concat([filtered_spectrum, metadata], axis=1).to_csv(
            f"{self._directory}/{self._filename}.csv",
            mode="a",
            index=False,
            header=False,
        )

        return spectrum_data, filtered_spectrum

    def finalize_csv(self):
        filepath = f"{self._directory}/{self._filename}.csv"
        df = pd.read_csv(filepath)

        for col in ["Center Freq", "Cavity Position"]:
            df[col] = df[col].dropna().reset_index(drop=True)

        df.to_csv(filepath, index=False)

        self.logger.logger.info(
            f"CSV data finalized: {self._directory}/{self._filename}.csv"
        )

    def update_settings(self, settings: Settings):
        self.settings = settings

    def update_config(self, config: Config):
        self.config = config

        self.zaber_controller.update_config(config)
        self.valon_controller.update_config(config)
        self.awg_controller.update_config(config)
        self.oscilloscope_controller.update_config(config)
        self.delay_generator_controller.update_config(config)

        self.logger.logger.info("Config updated")

    def init_device(self, device_name, config):
        try:
            getattr(self, device_name).initialize(config)
            success = True
        except Exception as e:
            self.logger.logger.error(f"Failed to initialize {device_name}: {e}")
            success = False

        return success

    def get_device_status(self):
        def _is_initialized(controller):
            return controller is not None and controller.is_initialized()

        return {
            "delay_generator": _is_initialized(self.delay_generator_controller),
            "zaber": _is_initialized(self.zaber_controller),
            "oscilloscope": _is_initialized(self.oscilloscope_controller),
            "valon": _is_initialized(self.valon_controller),
            "switch": _is_initialized(self.switch_controller),
            "awg": _is_initialized(self.awg_controller),
        }
