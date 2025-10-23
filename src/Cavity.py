import oscilloscopeController
import DelayGeneratorController
import zaberController


class Cavity:
    def __init__(self, srscontroller):
        self.__zaber_retune_speed = 101204
        self.srscontroller = srscontroller

    def retune_cavity_position(self, start_pos_zaber, start_pos_zaber_mm, zaber_speed):
        # Retuning of the cavity position
        self.srscontroller.set_freq(300)
        zaberController.zaberSetSpeed(
            self.__zaber_retune_speed
        )  # Speed for moving to the beginning spot, not the speed for scanning
        print(f"Moving Zaber to {start_pos_zaber_mm}")
        zaberController.moveToZaber(start_pos_zaber)
        zaberController.zaberDevice.poll_until_idle()
        zaberController.zaberSetSpeed(zaber_speed)
        oscilloscopeController.oscCalibStart()
        self.srscontroller.start_trig()

    def move_cavity_position(self, max_pos):
        # Moving to new cavity position for next data acquisition
        print("Moving to maximum position at: ", max_pos, " mm")
        zaberController.zaberSetSpeed(self.__zaber_retune_speed)
        zaberController.moveToZaber(int(max_pos * 20997))
        zaberController.zaberDevice.poll_until_idle()
        curr_pos = zaberController.zaberDevice.get_position()
        print("Running scan... Zaber is at position: ", curr_pos / 20997)
