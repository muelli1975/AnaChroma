"""External tools without shell interpolation or blocking the GUI."""
from __future__ import annotations
import subprocess
import tempfile
import time
from threading import Event
from .engine import check_cancel


def run_tool(arguments: list[str], cancel: Event | None, timeout: float) -> tuple[int, str]:
    check_cancel(cancel)
    # A file rather than an undrained pipe avoids deadlocks with chatty tools.
    with tempfile.TemporaryFile() as log:
        process = subprocess.Popen(arguments, stdout=log, stderr=log,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        started = time.monotonic()
        try:
            while process.poll() is None:
                check_cancel(cancel)
                if time.monotonic() - started > timeout:
                    raise TimeoutError("Das externe Programm hat das Zeitlimit überschritten.")
                if cancel is not None:
                    cancel.wait(.05)
                else:
                    time.sleep(.05)
            check_cancel(cancel)
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        length = log.tell()
        log.seek(max(0, length-8192))
        return process.returncode, log.read().decode("utf-8", errors="replace").strip()
