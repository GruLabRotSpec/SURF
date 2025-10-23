from zaber_motion.ascii import Connection


class Zaber:
    def __init__(self) -> None:
        port = Connection.open_serial_port("COM5")
        self.device = port.get_device(1)
        self.axis = self.device.get_axis(1)
        # self.device.send(f"/limit.max {zaberMax}")

    # moves Zaber to abs pos
    def moveToZaber(self, pos):
        zaberDevice.move_abs(pos)
        self.axis.move_absolute()
        Pos = zaberDevice.get_position()
        currPos = Pos / 20997
        print(f"Zaber is at position: {currPos}")

    def home(self):
        self.axis.home()

    # moves by relative pos, or distance from curr pos
    def moveByZaber(self, dist):
        zaberDevice.move_abs(dist)
        currPos = zaberDevice.get_position()
        print(f"Zaber is at position: {currPos}")

    # initializes movement at speed
    def zaberStart(zaberSpeed):
        zaberDevice.move_vel(zaberSpeed)

    def zaberSetSpeed(zaberSpeed):
        zaberDevice.send(f"/set maxspeed {zaberSpeed}")

    def zaberSetup(startPosZaber):
        zaberDevice.move_abs(startPosZaber)
        # zaberDevice.send(f"/set rel {endPosZaber}") #changed this
