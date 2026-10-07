from dataclasses import asdict, dataclass
import json
from pathlib import Path
from .presets import atomic_json


@dataclass
class Settings:
    last_input: str = ""
    output: str = ""
    recursive: bool = False


def load_settings(path: Path) -> Settings:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return Settings(str(data.get("last_input", "")), str(data.get("output", "")),
                        data.get("recursive", False) is True)
    except (OSError, ValueError, AttributeError):
        return Settings()


def save_settings(path: Path, settings: Settings) -> None:
    atomic_json(path, asdict(settings))
