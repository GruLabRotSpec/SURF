from spectrometer import Spectrometer

# This file is for basic testing and running of the spectrometer without the GUI
# Actual testing is done in the test/ directory

# Variables in arrows (<>) need to be replaced with actual values to run


def main():
    spectrometer = Spectrometer()

    # Test frequency scan
    def frequencyScan():
        spectrometer.scan_frequency(11200, 11100, 0.5)

    def cavitySearch():
        spectrometer.set_instrument_settings(1, None)       # First variable is speed while scanning
        spectrometer.cavity_search(9000, 0.5)

    # Test cavity search and frequency scan
    def cavitySearchAndFrequencyScan():
        spectrometer.set_instrument_settings(<zaber_speed>, <rf_level>)

        # Cavity search
        spectrometer.set_output_options(<folder_name>, <filename>)
        spectrometer.set_experiment_settings(<trig_rate>, <acq_rate>, <gate_pos>, <intensity>, <awg_freq>)
        spectrometer.cavity_search(<stop_freq>, <step_size>)

        # Frequency scan
        spectrometer.set_output_options(<folder_name>, <filename>)
        spectrometer.set_experiment_settings(<trig_rate>, <acq_rate>, <gate_pos>, <intensity>, <awg_freq>)
        spectrometer.scan_frequency(<start_freq>, <stop_freq>, <step_size>)


    # Enter statements to run the above functions below this line

    # cavitySearchAndFrequencyScan()

    # Enter statemetns to run the above functions above this line

if __name__ == "__main__":
    main()
