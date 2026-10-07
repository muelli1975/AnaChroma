from __future__ import annotations
from dataclasses import dataclass
import os
from pathlib import Path
import re
from threading import Event
import numpy as np
from PIL import Image, ImageOps

from .engine import check_cancel

EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp", ".webp"}


@dataclass(frozen=True)
class InputList:
    files: tuple[Path, ...]
    root: Path
    folder_input: bool
    selected: int = 0


def discover(path: Path, recursive: bool = False, exclude: tuple[Path, ...] = (),
             cancel: Event | None = None) -> InputList:
    path = path.resolve()
    is_file = path.is_file()
    if is_file and path.suffix.lower() not in EXTENSIONS:
        raise ValueError("Dieses Eingabeformat wird nicht unterstützt.")
    root = path.parent if is_file else path
    if not root.is_dir():
        raise ValueError("Der Eingabeordner existiert nicht.")
    excluded = tuple(p.resolve() for p in exclude)
    # Never exclude the whole source when output equals source. Named generated
    # subfolders are excluded, and each export uses a frozen discovery snapshot.
    def blocked(p):
        return any(p == q or q in p.parents for q in excluded if q != root)
    files = []
    for directory, dirs, names in os.walk(root, followlinks=False):
        check_cancel(cancel)
        d = Path(directory)
        dirs[:] = [n for n in dirs if n not in {"output", "tmp", "_temp"} and not blocked(d/n)]
        for name in names:
            p = d/name
            if p.suffix.lower() in EXTENSIONS and not blocked(p) and p.is_file():
                files.append(p)
        if not recursive:
            break
    def key(p):
        return tuple((0, int(t)) if t.isdigit() else (1, t.casefold())
                     for t in re.split(r"(\d+)", str(p.relative_to(root))))
    files.sort(key=key)
    if is_file and path not in files:
        files.append(path)
        files.sort(key=key)
    if not files:
        raise ValueError("Keine unterstützten Bilder gefunden.")
    return InputList(tuple(files), root, not is_file, files.index(path) if is_file else 0)


def load_pair(path: Path, max_edge: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    with Image.open(path) as source:
        oriented = ImageOps.exif_transpose(source)
        rgb = oriented.convert("RGB")
        if rgb.width % 2:
            raise ValueError("Bildbreite ist nicht gerade – SBS kann nicht sauber geteilt werden.")
        if rgb.width < 2:
            raise ValueError("Das SBS-Bild ist zu schmal.")
        half = rgb.width // 2
        left, right = rgb.crop((0, 0, half, rgb.height)), rgb.crop((half, 0, rgb.width, rgb.height))
        if max_edge and max(left.size) > max_edge:
            ratio = max_edge / max(left.size)
            size = (max(1, round(left.width*ratio)), max(1, round(left.height*ratio)))
            left = left.resize(size, Image.Resampling.LANCZOS)
            right = right.resize(size, Image.Resampling.LANCZOS)
        return np.array(left), np.array(right)
