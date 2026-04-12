from pydantic import BaseModel
import tomllib
import tomli_w
from pathlib import Path
from typing import Literal


class ValonConfig(BaseModel):
    rf_output: bool
    rf_level: int
    valon_port: str
    synth_power: bool
    ref_source: Literal["Internal","External"]
    ref_freq: float


class ZaberConfig(BaseModel):
    zaber_scanning_speed: float
    zaber_moving_speed: float
    zaber_step_size: float
    zaber_port: str


class AWGConfig(BaseModel):
    awg_status: bool
    awg_freq: int
    awg_run_mode: str
    awg_ch_1_output: bool
    awg_ch_2_output: bool


class MathConfig(BaseModel):
    window: Literal["Rectangular", "Hamming", "Hanning", "Blackman"]
    resolution: float
    gate_position: float


class OscilloscopeConfig(BaseModel):
    channel: str
    acq_rate: int
    sample_rate: int
    math_averages: int
    visa_address: str
    math3: MathConfig
    math4: MathConfig


class DelayGeneratorConfig(BaseModel):
    trigger_rate: float


class Config(BaseModel):
    valon_controller: ValonConfig
    zaber_controller: ZaberConfig
    awg_controller: AWGConfig
    oscilloscope_controller: OscilloscopeConfig
    delay_generator_controller: DelayGeneratorConfig


def load_config(config_path: Path) -> Config:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "rb") as f:
        config_dict = tomllib.load(f)

    return Config(**config_dict)


def save_config(save_path: Path, config: Config):
    with open(save_path, "wb") as f:
        tomli_w.dump(config.model_dump(), f)
