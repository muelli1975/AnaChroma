from __future__ import annotations
from pathlib import Path
from threading import Event
from PIL import Image
from .engine import Cancelled
from .processes import run_tool
from .resources import find_tool


def copy_metadata(source: Path, target: Path, cancel: Event | None = None) -> str:
    """Return an empty string on success, a non-fatal warning on failure."""
    executable = find_tool("exiftool")
    if executable is None:
        return "ExifTool nicht gefunden; JPEG wurde ohne Originalmetadaten gespeichert."
    try:
        with Image.open(target) as image:
            w, h = image.size
        arguments = [str(executable), "-overwrite_original", "-TagsFromFile", str(source),
                     "--Preview:all", "--Orientation", "--MPF:all", "--ICC_Profile:all",
                     "--ColorSpace", "-EXIF:ColorSpace=1", f"-EXIF:ExifImageWidth={w}",
                     f"-EXIF:ExifImageHeight={h}", str(target)]
        code, detail = run_tool(arguments, cancel, 30.)
        return f"Metadaten konnten nicht vollständig übernommen werden: {detail}" if code else ""
    except Cancelled:
        raise
    except (OSError, TimeoutError) as exc:
        return f"Metadaten konnten nicht übernommen werden: {exc}"
