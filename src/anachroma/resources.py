from __future__ import annotations
import os
from pathlib import Path
import shutil
import sys


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resource_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", app_dir()))


def user_dir() -> Path:
    # Portable first; installed/read-only builds fall back to user configuration.
    root = app_dir()
    if os.access(root, os.W_OK):
        return root
    if sys.platform == "win32":
        return Path(os.environ.get("APPDATA", Path.home())) / "AnaChroma"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "AnaChroma"
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "anachroma"


def find_tool(name: str) -> Path | None:
    names = (f"{name}.exe", name) if sys.platform == "win32" else (name,)
    for root in dict.fromkeys((app_dir(), resource_dir())):
        for executable in names:
            for relative in (Path("tools") / executable, Path("tools") / name / executable):
                candidate = root / relative
                if candidate.is_file() and (sys.platform == "win32" or os.access(candidate, os.X_OK)):
                    return candidate
    for executable in names:
        found = shutil.which(executable)
        if found:
            return Path(found)
    return None
