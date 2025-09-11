#for zaber:
from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply
import time

#first, intialize from main
#then, use functions as needed
zaberMax = 50
#initialize zaber as global
def initializeZaber(zaberMax=40):
    global zaberDevice
    port = AsciiSerial("COM5")
    zaberDevice = AsciiDevice(port, 1)
    zaberDevice.send(f'/limit.max {zaberMax}')
    #homeZaber()
    print("________________________________")
    print("Zaber initialized at port: ", port)
    print("________________________________")
    return zaberDevice

#sends Zaber to home (0mm)     
def homeZaber():
    zaberDevice.home()

#moves Zaber to abs pos
def moveToZaber(pos):
    zaberDevice.move_abs(pos)
    Pos = zaberDevice.get_position()
    currPos = Pos/20997
    print(f"Zaber is at position: {currPos}")

#moves by relative pos, or distance from curr pos
def moveByZaber(dist):
    zaberDevice.move_abs(dist)
    currPos = zaberDevice.get_position()
    print(f"Zaber is at position: {currPos}")

#def zaberSetup(startPosZaber, ZaberMax):
#    zaberDevice.move_abs(startPosZaber)
#    zaberDevice.send(f"/set limit.max {ZaberMax}")

#initializes movement at speed
def zaberStart(zaberSpeed):
    zaberDevice.move_vel(zaberSpeed)

def zaberSetSpeed(zaberSpeed):
    zaberDevice.send(f"/set maxspeed {zaberSpeed}")



def zaberSetup(startPosZaber):
    zaberDevice.move_abs(startPosZaber)
    #zaberDevice.send(f"/set rel {endPosZaber}") #changed this


