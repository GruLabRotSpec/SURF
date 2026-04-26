from enum import Enum


class DeviceStatus(Enum):
    CONNECTING = "connecting"
    ONLINE = "online"
    OFFLINE = "offline"
