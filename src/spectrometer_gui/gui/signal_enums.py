from enum import Enum
from dataclasses import dataclass


class ScanType(Enum):
    NONE = 0
    FREQUENCY = 1
    CAVITY = 2

class CavitySearchType(Enum):
    CONTINUOUS = "continuous"
    PULSED = "pulsed"

@dataclass
class GraphState:
    scan_type: ScanType
    cavityFREQ: list
    cavityINT: list
    cavitypos: list
    fft_x: list
    fft_y: list

@dataclass
class CavityGraphState:
    x_peaks: list
    y_peaks: list

class ZaberSpeed(Enum):
    SCANNING = 0
    MOVING = 1

class DeviceStatus(Enum):
    CONNECTING = "connecting"
    ONLINE = "online"
    OFFLINE = "offline"
