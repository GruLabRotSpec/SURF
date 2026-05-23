from pydantic import BaseModel
import tomllib
import tomli_w
from pathlib import Path
from typing import Literal

class Experiment(BaseModel):
    sample_name: str
    sample_temp: float
    gas: str
    gas_width: float
    backing_pressure: float
    chamber_pressure: str
    mw_width: float

def save_config(save_path: Path, experiment: Experiment):
    with Path.open(save_path, "wb") as f:
        tomli_w.dump(experiment.model_dump(), f)
