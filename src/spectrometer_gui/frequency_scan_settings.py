from dataclasses import dataclass


@dataclass
class Experiment:
    sample_name: str
    sample_temp: float
    gas_name: str
    gas_width: float
    backing_pressure: float
    chamber_pressure: str
    mw_width: float


@dataclass
class ScanParameters:
    start_freq: float
    end_freq: float
    step_size: float
    scanning_speed: float
    zaber_pos: float | None
    acq_num: int


@dataclass
class DigitizerSettings:
    resolution: int
    acq_window: int
    apodization: str


@dataclass
class TimingSettings:
    rep_rate: int
    valve_mw_delay: int
    spdt_width: float
    acq_delay: int

@dataclass
class OutputSettings:
    filename: str
    location: str


@dataclass
class FrequencyScanSettings:
    experiment: Experiment
    scan_parameters: ScanParameters
    digitizer_settings: DigitizerSettings
    timing_settings: TimingSettings
    output_settings: OutputSettings
