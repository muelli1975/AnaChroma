from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path
import tempfile
from threading import Event
from typing import Callable
from PIL import Image, ImageCms

from .cielab import make_cielab
from .engine import check_cancel, make_anaglyph
from .inputs import InputList, load_pair
from .matrices import Method
from .metadata import copy_metadata

SIZE_LABELS = ("Original", "1080p", "2160p", "2048 lange Seite", "Benutzerdefiniert")


@dataclass(frozen=True)
class SizeSpec:
    kind: str = "Original"
    edge: str = "long"
    pixels: int = 2048

    def dimensions(self, size: tuple[int, int]) -> tuple[int, int]:
        w, h = size
        if self.kind == "Original":
            return size
        if self.kind == "1080p":
            factor = min(1920/w, 1080/h)
        elif self.kind == "2160p":
            factor = min(3840/w, 2160/h)
        elif self.kind == "2048 lange Seite":
            factor = 2048/max(w, h)
        elif self.kind == "Benutzerdefiniert":
            if self.edge not in {"long", "short"} or isinstance(self.pixels, bool) or self.pixels < 1:
                raise ValueError("Eine positive Pixelzahl und lange/kurze Seite wählen.")
            factor = self.pixels/(max(w, h) if self.edge == "long" else min(w, h))
        else:
            raise ValueError("Unbekannte Ausgabegröße.")
        # Match the Batch's ability to upscale; round to the nearest whole pixel.
        return max(1, round(w*factor)), max(1, round(h*factor))


def resize(image: Image.Image, spec: SizeSpec) -> Image.Image:
    size = spec.dimensions(image.size)
    return image if size == image.size else image.resize(size, Image.Resampling.LANCZOS)


def target_paths(inputs: InputList, files: tuple[Path, ...], output: Path, method: Method) -> tuple[Path, ...]:
    method.validate()
    targets = []
    seen = set()
    sources = {str(p.resolve()).casefold() for p in inputs.files}
    for source in files:
        relative = source.relative_to(inputs.root)
        folder = relative.parent
        target = output / folder / f"{source.stem}_{method.suffix}.jpg"
        key = str(target.resolve()).casefold()
        if key in seen:
            raise ValueError(f"Mehrere Eingaben würden dieselbe Ausgabedatei erzeugen: {target.name}")
        if key in sources:
            raise ValueError("Eine Ausgabedatei würde ein ausgewähltes Original überschreiben.")
        seen.add(key)
        targets.append(target)
    return tuple(targets)


@dataclass(frozen=True)
class ExportJob:
    source: Path
    target: Path
    method: Method


def export_jobs(inputs: InputList, files: tuple[Path, ...], output: Path,
                methods: tuple[Method, ...]) -> tuple[ExportJob, ...]:
    """Freeze the complete job and detect collisions before any files are written."""
    if not methods:
        raise ValueError("Bitte mindestens ein Ausgabeverfahren auswählen.")
    by_method = [target_paths(inputs, files, output, method) for method in methods]
    jobs = tuple(ExportJob(source, targets[i], method)
                 for i, source in enumerate(files) for method, targets in zip(methods, by_method))
    destinations = [str(job.target.resolve()).casefold() for job in jobs]
    if len(set(destinations)) != len(destinations):
        raise ValueError("Ausgabeverfahren würden dieselbe Datei erzeugen.")
    return jobs


@lru_cache(maxsize=1)
def srgb_profile() -> bytes:
    return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def export_image(source: Path, target: Path, method: Method, size: SizeSpec,
                 quality: int = 90, cancel: Event | None = None,
                 status: Callable[[str], None] = lambda _: None) -> str:
    if quality not in {90, 95}:
        raise ValueError("JPEG-Qualität muss 90 oder 95 sein.")
    check_cancel(cancel)
    status("Lade SBS...")
    left, right = load_pair(source)
    check_cancel(cancel)
    status("Berechne Anaglyphe...")
    if method.mode == "cielab":
        left = resize(Image.fromarray(left), size)
        right = resize(Image.fromarray(right), size)
        import numpy as np
        image = make_cielab(np.array(left), np.array(right), cancel)
    else:
        image = resize(Image.fromarray(make_anaglyph(left, right, method, cancel)), size)
    check_cancel(cancel)
    status("Speichere JPEG...")
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{target.stem}.", suffix=".partial.jpg", dir=target.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        image.save(temporary, "JPEG", quality=quality, subsampling=0, optimize=True, icc_profile=srgb_profile())
        check_cancel(cancel)
        status("Übernehme Metadaten...")
        warning = copy_metadata(source, temporary, cancel)
        check_cancel(cancel)
        os.replace(temporary, target)
        return warning
    finally:
        temporary.unlink(missing_ok=True)
