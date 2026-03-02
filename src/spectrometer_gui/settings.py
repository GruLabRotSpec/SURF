from pydantic import BaseModel
import tomllib
from pathlib import Path
from typing import Literal


class OutputConfig(BaseModel):
    location: str
    filename: str


class LoggingConfig(BaseModel):
    enabled: bool
    location: str


class Settings(BaseModel):
    output: OutputConfig
    logging: LoggingConfig


def load_settings(settings_path) -> Settings:
    toml_path = Path(settings_path)

    if not toml_path.exists():
        raise FileNotFoundError(f"Config file not found: {toml_path}")

    with open(toml_path, "rb") as f:
        settings_dict = tomllib.load(f)

    return Settings(**settings_dict)

def save_settings(save_path: Path, settings: Settings):
    with open(save_path, "wb") as f:
        tomli_w.dump(config.model_dump(), f)
