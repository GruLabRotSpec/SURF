import qdarktheme
from pathlib import Path


def _load_stylesheet(name: str) -> str:
    path = Path(__file__).parent / "stylesheets" / f"{name}.qss"
    return path.read_text() if path.exists() else ""


def apply_theme(theme: str):
    additional_qss = _load_stylesheet("general") + _load_stylesheet(theme)
    qdarktheme.setup_theme(theme, additional_qss=additional_qss)


def get_themes():
    return qdarktheme.get_themes()
