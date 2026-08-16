from dataclasses import dataclass
from gui.signal_enums import CavitySearchType

@dataclass
class CavitySearchSettings:
    cavity_type: CavitySearchType
    freq: float
    step_size: float
    zaber_speed: float
