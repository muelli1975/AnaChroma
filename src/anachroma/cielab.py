from __future__ import annotations
from pathlib import Path
from threading import Event
import tempfile
import numpy as np
from PIL import Image

from .engine import check_cancel
from .processes import run_tool
from .resources import find_tool


def make_cielab(left: np.ndarray, right: np.ndarray, cancel: Event | None = None,
                executable: Path | None = None) -> Image.Image:
    executable = executable or find_tool("cielab")
    if executable is None:
        raise FileNotFoundError("CIELab nicht gefunden. Das externe Programm unter tools/cielab bereitstellen.")
    check_cancel(cancel)
    with tempfile.TemporaryDirectory(prefix="anachroma-cielab-") as name:
        directory = Path(name)
        l, r, out = (directory/n for n in ("left.png", "right.png", "output.png"))
        Image.fromarray(left).save(l)
        Image.fromarray(right).save(r)
        check_cancel(cancel)
        code, detail = run_tool([str(executable), str(l), str(r), "-o", str(out)], cancel, 600.)
        if code or not out.is_file():
            raise RuntimeError(f"CIELab konnte das Bild nicht berechnen: {detail or f'Exit-Code {code}'}")
        with Image.open(out) as result:
            if result.size != (left.shape[1], left.shape[0]):
                raise ValueError("CIELab lieferte eine unerwartete Bildgröße.")
            return result.convert("RGB")
