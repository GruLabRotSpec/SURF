import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
import os


import plot as plotter


from delay_generator_controller import DelayGeneratorController
from zaber_controller import ZaberController
from oscilloscope_controller import OscilloscopeController
from valon_controller import ValonController
from Cavity import Cavity  # Remove this class later


class Spectrometer:
    def __init__(self):
        self.__status = "Idle"
        self.__delay_generator_controller = None
        self.__zaber_controller = None
        self.__oscilloscope_controller = None
        self.__valon_controller = None

        try:
            self.__delay_generator_controller = DelayGeneratorController()
            self.__zaber_controller = ZaberController(0.003)
            self.__oscilloscope_controller = OscilloscopeController()
            self.__valon_controller = ValonController("COM3")
            self.__cavity = Cavity.Cavity(
                self.__zaber_controller,
                self.__oscilloscope_controller,
                self.__delay_generator_controller,
            )
        except PermissionError:
            print(
                "ATTN: Permission Error. Make sure Valon and Zaber windows are closed."
            )
            exit()

    def get_status(self):
        return self.__status

    def __set_status(self, status):
        self.__status = status

    def scan_frequency(start_freq, stop_freq, step_size):
        return

    def cavity_search():
        return

    def __zaber__thread(self):
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

    def __fft_from_scope():
        global time_scale, time_start, vertical_scale, vertical_offset, vertical_position, freq_cent, freq_span

        wave_values = self.__oscilloscope_controller.acq_ft_curve(channel, time_delay)

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
        x_values, y_values = self.__scale_fft(wave_values, start)

        plotter.generate_plot(x_values, y_values)

        return x_values, y_values

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
        return newfft_x_values, newfft_y_values
