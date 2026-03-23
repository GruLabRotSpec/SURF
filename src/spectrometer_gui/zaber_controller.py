from config import Config

from zaber_motion.ascii import Connection
from zaber_motion.units import Units
from enum import Enum


class ZaberSpeed(Enum):
    SCANNING = 0
    HOMING = 1


class ZaberController:
    def __init__(self) -> None:
        self.initialized = False

    def initialize(self, config: Config):
        port = Connection.open_serial_port(config.zaber_controller.zaber_port)
        port.detect_devices()  # Requires Internet connection on first run, then caches
        self.device = port.get_device(1)
        self.axis = self.device.get_axis(1)

        self.update_config(config)

        if not self.axis.is_homed():
            print("Zaber not Homed, Homing")
            self.home(False)

        self.initialized = True

    def is_initialized(self) -> bool:
        return self.initialized  # Check device connection here instead

    def update_config(self, config: Config):
        zaber_config = config.zaber_controller

        self.move_speed = zaber_config.zaber_speed
        self.homing_speed = zaber_config.zaber_homing_speed
        self.step_size = zaber_config.zaber_step_size

        self.current_speed = self.move_speed

    def move_to(self, pos, blocking=True):
        self.axis.move_absolute(
            pos,
            Units.LENGTH_MILLIMETRES,
            wait_until_idle=blocking,
            velocity=self.current_speed,
            velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND,
        )

    def get_pos(self) -> float:
        return self.axis.get_position(Units.LENGTH_MILLIMETRES)

    def home(self, blocking=True):
        self.axis.home(wait_until_idle=blocking)

    def set_speed(self, zaber_speed: ZaberSpeed):
        if zaber_speed == ZaberSpeed.SCANNING:
            self.current_speed = self.move_speed
        elif zaber_speed == ZaberSpeed.HOMING:
            self.current_speed = self.homing_speed
