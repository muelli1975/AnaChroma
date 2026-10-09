from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile

from .matrices import BUILTINS, Method

SCHEMA_VERSION = 1


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def validate_presets(methods: list[Method]) -> None:
    ids = {m.id for m in BUILTINS}
    suffixes = {m.suffix for m in BUILTINS}
    names = set()
    for m in methods:
        m.validate()
        if m.builtin or not m.id.startswith("custom:") or not m.editable:
            raise ValueError("Ungültige Kennung oder Rechenfolge eines eigenen Verfahrens.")
        if m.id in ids or m.suffix in suffixes or m.name.casefold() in names:
            raise ValueError("Name, Kennung oder Dateinamenssuffix ist bereits vergeben.")
        ids.add(m.id)
        suffixes.add(m.suffix)
        names.add(m.name.casefold())


def load_presets(path: Path, notices: list[str] | None = None) -> list[Method]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload["schema_version"] != SCHEMA_VERSION:
            raise ValueError("Unbekannte Preset-Version; Datei wurde nicht verändert.")
        methods = []
        adjusted = []
        for entry in payload["presets"]:
            entry = dict(entry)
            if entry.get("brightness", 1.0) != 1.0 or entry.get("contrast", 1.0) != 1.0:
                adjusted.append(str(entry.get("name", "")))
            entry.pop("brightness", None)
            entry.pop("contrast", None)
            entry["left"] = tuple(tuple(row) for row in entry["left"])
            entry["right"] = tuple(tuple(row) for row in entry["right"])
            entry["powers"] = tuple(entry["powers"])
            methods.append(Method(**entry))
        validate_presets(methods)
        if notices is not None:
            notices.extend(adjusted)
        return methods
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        raise ValueError(f"Eigene Verfahren konnten nicht geladen werden: {exc}") from exc


def save_presets(path: Path, methods: list[Method]) -> None:
    validate_presets(methods)
    # Preserve a development preset file before removing its old adjustments.
    # Exclusive creation keeps every earlier backup intact.
    if path.exists():
        original = path.read_bytes()
        payload = json.loads(original)
        if any("brightness" in entry or "contrast" in entry for entry in payload.get("presets", [])):
            backup = path.with_name(path.name + ".pre-1.0.bak")
            index = 1
            while backup.exists() and backup.read_bytes() != original:
                backup = path.with_name(path.name + f".pre-1.0.{index}.bak")
                index += 1
            if not backup.exists():
                with backup.open("xb") as stream:
                    stream.write(original)
    atomic_json(path, {"schema_version": SCHEMA_VERSION, "presets": [asdict(m) for m in methods]})
