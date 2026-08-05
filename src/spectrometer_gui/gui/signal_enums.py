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
class GraphState:   #spectrum for frequency scan panel 
    scan_type: ScanType
    frequency: float
    fft_x: list
    fft_y: list
@dataclass
class CavityTrackState: #for cavity track on frequency scan panel 
    scan_type: ScanType
    cavityFreq: list
    cavityInt: list
    cavitypos: list

@dataclass
class ExperimentProgress:
    current_freq: float
    elapsed_time: str
    time_remaining: str

@dataclass
class CavityGraphState: #for cavity map
    scan_type: ScanType
    frequency: float
    x_pos: list
    y_int: list

class ZaberSpeed(Enum):
    SCANNING = 0
    MOVING = 1

class DeviceStatus(Enum):
    CONNECTING = "connecting"
    ONLINE = "online"
    OFFLINE = "offline"
