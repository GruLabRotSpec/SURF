from spectrometer import Spectrometer


def main():
    spectrometer = Spectrometer()

    # Test frequency scan
    spectrometer.scan_frequency(None, 11200, 0.5)


if __name__ == "__main__":
    main()
