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
from Cavity import Cavity # Remove this class later

class Spectrometer:
    def __init__(self):
        self.__status = "Idle"
        self.__delay_generator_controller = None
        self.__zaber_controller = None
        self.__oscilloscope_controller = None
        self.__valon_controller = None


    def get_status(self):
        return self.__status

    def __set_status(self, status):
        self._status = status

    def scan_frequency(start_freq, stop_freq, step_size):
        return

    def cavity_search():
        return
