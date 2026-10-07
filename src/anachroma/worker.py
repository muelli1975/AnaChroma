from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from queue import Queue
from threading import Condition, Event, Thread
from typing import Callable
from PIL import Image

from .cielab import make_cielab
from .engine import Cancelled, check_cancel, make_anaglyph
from .export import SizeSpec, export_image
from .inputs import load_pair
from .matrices import Method


class PreviewWorker:
    """Single latest-request slot; old work is cancelled, no growing queue."""
    def __init__(self, events: Queue):
        self.events = events
        self.condition = Condition()
        self.pending = None
        self.active_cancel = Event()
        self.closed = False
        self.cached_key = None
        self.cached_pair = None
        self.thread = Thread(target=self._run, daemon=True, name="anachroma-preview")
        self.thread.start()

    def request(self, identifier: int, path: Path, method: Method, max_edge: int = 1024) -> None:
        with self.condition:
            self.active_cancel.set()
            self.pending = (identifier, path, method, max_edge)
            self.condition.notify()

    def close(self) -> None:
        with self.condition:
            self.closed = True
            self.pending = None
            self.active_cancel.set()
            self.condition.notify()

    def _run(self) -> None:
        while True:
            with self.condition:
                self.condition.wait_for(lambda: self.closed or self.pending is not None)
                if self.closed:
                    return
                identifier, path, method, max_edge = self.pending
                self.pending = None
                cancel = self.active_cancel = Event()
            try:
                info = path.stat()
                key = (path.resolve(), info.st_mtime_ns, info.st_size, max_edge)
                if key != self.cached_key:
                    pair = load_pair(path, max_edge=max_edge)
                    check_cancel(cancel)
                    self.cached_pair, self.cached_key = pair, key
                left, right = self.cached_pair
                if method.mode == "cielab":
                    image = make_cielab(left, right, cancel)
                else:
                    image = Image.fromarray(make_anaglyph(left, right, method, cancel))
                check_cancel(cancel)
                self.events.put(("preview", identifier, image))
            except Cancelled:
                pass
            except Exception as exc:
                if not cancel.is_set():
                    self.events.put(("preview_error", identifier, str(exc)))


@dataclass
class BatchResult:
    processed: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    cancelled: bool = False


def run_batch(files: tuple[Path, ...], targets: tuple[Path, ...], method: Method,
              size: SizeSpec, quality: int, cancel: Event,
              report: Callable[[tuple], None]) -> BatchResult:
    if len(files) != len(targets):
        raise ValueError("Für jedes Eingabebild wird genau ein Ausgabeziel benötigt.")
    result = BatchResult()
    for index, (source, target) in enumerate(zip(files, targets), 1):
        try:
            check_cancel(cancel)
            report(("batch_progress", index, len(files), source.name, "Lade SBS..."))
            warning = export_image(source, target, method, size, quality, cancel,
                lambda message: report(("batch_progress", index, len(files), source.name, message)))
            result.processed += 1
            if warning:
                result.warnings.append(f"{source.name}: {warning}")
            report(("batch_file_done", index, len(files)))
        except Cancelled:
            result.cancelled = True
            break
        except Exception as exc:
            result.errors.append(f"{source.name}: {exc}")
            report(("batch_file_done", index, len(files)))
    return result
