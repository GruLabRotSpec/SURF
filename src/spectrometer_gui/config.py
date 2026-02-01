from pydantic import BaseModel
import tomllib
from pathlib import Path
from typing import Literal


class ValonConfig(BaseModel):
    rf_level: int  # TODO, Figure out if this is actually int only


class ZaberConfig(BaseModel):
    zaber_speed: float  # TODO: Limit the speed to the possible range
    zaber_homing_speed: float


class AWGConfig(BaseModel):
    awg_status: bool
    awg_freq: int
    awg_run_mode: str
    awg_ch_1_output: bool
    awg_ch_2_output: bool


class OscilloscopeConfig(BaseModel):
    resolution: float
    sample_rate: float
    window_type: Literal["Rectangular", "Hamming", "Hanning", "Blackman"]
    gate_position: float
    math_averages: int


class DelayGeneratorConfig(BaseModel):
    trigger_rate: str  # This probably needs to be changed


class Config(BaseModel):
    valon_controller: ValonConfig
    zaber_controller: ZaberConfig
    awg_controller: AWGConfig
    delay_generator_controller: DelayGeneratorConfig
    oscilloscope_controller: OscilloscopeConfig


def load_config(config_path) -> Config:
    toml_path = Path(config_path)

    if not toml_path.exists():
        raise FileNotFoundError(f"Config file not found: {toml_path}")

    with open(toml_path, "rb") as f:
        config_dict = tomllib.load(f)

    return Config(**config_dict)
