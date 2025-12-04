from zaber_motion.ascii import Connection
from zaber_motion.units import Units


class ZaberController:
    def __init__(self, max_speed, port = "COM5") -> None:
        port = Connection.open_serial_port(port)
        print(port.detect_devices())
        self.device = port.get_device(1)
        self.axis = self.device.get_axis(1)
        self.max_speed = max_speed

    def move_to(self, pos):
        self.axis.move_absolute(pos, Units.LENGTH_MILLIMETRES, velocity=self.max_speed, 
                                velocity_unit=Units.VELOCITY_MILLIMETRES_PER_SECOND)

    def get_pos(self) -> float:
        return self.axis.get_position(Units.LENGTH_MILLIMETRES)

    def home(self):
        self.axis.home()

    def set_speed(self, speed):
        self.max_speed = speed