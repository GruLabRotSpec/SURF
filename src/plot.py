import matplotlib.pyplot as plt

def plot_position_vs_intensity(plot = plt, pos_arr, max_lists):
    plot.plot(pos_arr, max_lists)
    plot.title("Zaber Position vs. Intensity")
    plot.xlabel("Zaber Position (mm)")
    plot.ylabel("Intensity (Volts)")
    plot.show(block=False)
    plot.pause(3)
    plot.close()

def generate_plot(x_wave, y_wave):
    plt.plot(x_wave, y_wave)
    plt.title("Data")
    plt.xlabel("Frequency")
    plt.ylabel("Relative Intensity")
    plt.show(block=False)
    plt.pause(3)
    plt.close()
    return
