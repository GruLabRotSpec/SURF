from enum import Enum
from dataclasses import dataclass


class ScanType(Enum):
    NONE = 0
    FREQUENCY = 1
    CAVITY = 2


@dataclass
class GraphState:
    scan_type: ScanType
    pos_array: list
    max_list: list
    frequency: float
    fft_x: list
    fft_y: list

class ZaberSpeed(Enum):
    SCANNING = 0
    MOVING = 1

class DeviceStatus(Enum):
    CONNECTING = "connecting"
    ONLINE = "online"
    OFFLINE = "offline"
