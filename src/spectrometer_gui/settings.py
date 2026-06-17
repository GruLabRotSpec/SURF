from pydantic import BaseModel, Field
import tomllib
import tomli_w
from pathlib import Path


class OutputConfig(BaseModel):
    location: str
    filename: str


class LoggingConfig(BaseModel):
    enabled: bool
    location: str


class ScopePresetItem(BaseModel):
    name: str
    path: str


class ScopePreset(BaseModel):
    root_path: str
    presets: dict[str, ScopePresetItem] = Field(default_factory=dict)


class Settings(BaseModel):
    output: OutputConfig
    logging: LoggingConfig
    scope_preset: ScopePreset
    theme: str = "auto"


def load_settings(settings_path) -> Settings:
    toml_path = Path(settings_path)

    if not toml_path.exists():
        default_path = Path(__file__).parent / "defaults" / "default_settings.toml"
        if default_path.exists():
            toml_path = default_path
        else:
            raise FileNotFoundError(
                f"Config file not found: {toml_path} and no default_settings.toml found"
            )

    with Path.open(toml_path, "rb") as f:
        settings_dict = tomllib.load(f)

    return Settings(**settings_dict)


def save_settings(save_path: Path, settings: Settings):
    with Path.open(save_path, "wb") as f:
        tomli_w.dump(settings.model_dump(), f)
