from enum import Enum

class ZaberSpeed(Enum):
    SCANNING = 0
    MOVING = 1

class DeviceStatus(Enum):
    CONNECTING = "connecting"
    ONLINE = "online"
    OFFLINE = "offline"
