import matplotlib.pyplot as plt

def plot_position_vs_intensity(pos_arr, max_lists):
    plt.plot(pos_arr, max_lists)
    plt.title("Zaber Position vs. Intensity")
    plt.xlabel("Zaber Position (mm)")
    plt.ylabel("Intensity (Volts)")
    plt.show(block=False)
    plt.pause(3)
    plt.close()

def generate_plot(x_wave, y_wave):
    plt.plot(x_wave, y_wave)
    plt.title("Data")
    plt.xlabel("Frequency")
    plt.ylabel("Relative Intensity")
    plt.show(block=False)
    plt.pause(3)
    plt.close()
    return
