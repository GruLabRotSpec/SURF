from config import Config

from zaber_motion.ascii import Connection
from zaber_motion.units import Units


class ZaberController:
    def __init__(self) -> None:
        self.initialized = False

    def initialize(self, config: Config):
        port = Connection.open_serial_port(config.zaber_controller.zaber_port)

        self.device = port.get_device(1)
        self.axis = self.device.get_axis(1)

        self.initialized = True

    def is_initialized(self) -> bool:
        return self.initialized  # Check device connection here instead

    def update_config(self, config: Config):
        zaber_config = config.zaber_controller

        self.move_speed = zaber_config.zaber_speed
        self.homing_speed = zaber_config.zaber_homing_speed

    def move_to(self, pos):
        self.axis.move_absolute(
            pos,
            Units.LENGTH_MILLIMETRES,
            velocity=self.max_speed,
            velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
        )

    def get_pos(self) -> float:
        return self.axis.get_position(Units.LENGTH_MILLIMETRES)

    def home(self):
        self.axis.home()

    def set_speed(self, speed):
        self.max_speed = speed
