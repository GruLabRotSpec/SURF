from delay_generator_controller import DelayGeneratorController
from zaber_controller import ZaberController, ZaberSpeed
from oscilloscope_controller import OscilloscopeController


class Cavity:
    def __init__(
        self,
        zaber: ZaberController,
        oscilloscope: OscilloscopeController,
        srscontroller: DelayGeneratorController,
    ):
        self.__zaber_retune_speed = 4.8
        self.zaber = zaber
        self.oscilloscope = oscilloscope
        self.srscontroller = srscontroller

    def retune_cavity_position(self, start_pos_zaber, zaber_speed):
        # Retuning of the cavity position
        self.srscontroller.set_frequency(300)
        self.zaber.set_speed(ZaberSpeed.HOMING)
        # Speed for moving to the beginning spot, not the speed for scanning
        print(f"Moving Zaber to {start_pos_zaber}")
        self.zaber.move_to(start_pos_zaber)
        self.zaber.set_speed(ZaberSpeed.SCANNING)
        self.oscilloscope.calib_start()
        self.srscontroller.start_trig()

    def move_cavity_position(self, max_pos):
        # Moving to new cavity position for next data acquisition
        print("Moving to maximum position at: ", max_pos, " mm")
        self.zaber.set_speed(ZaberSpeed.SCANNING)
        self.zaber.move_to(max_pos)
        curr_pos = self.zaber.get_pos()
        print("Running scan... Zaber is at position: ", curr_pos)
