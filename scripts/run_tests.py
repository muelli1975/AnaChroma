"""Run every test, isolating native Tk lifetimes between GUI checks."""
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
GUI_TESTS = "tests/test_gui.py"


def pytest(*args, **kwargs):
    return subprocess.run(
        [sys.executable, "-m", "pytest", "--color=no", *args],
        cwd=ROOT, check=True, **kwargs,
    )


def main():
    pytest("-q", f"--ignore={GUI_TESTS}")
    collected = pytest("--collect-only", "-q", GUI_TESTS,
                       capture_output=True, text=True, encoding="utf-8")
    checks = [line.strip() for line in collected.stdout.splitlines()
              if line.startswith(GUI_TESTS + "::")]
    if not checks:
        raise RuntimeError("No native GUI checks collected: " + collected.stdout)
    # Recreating Tk roots in a shared Windows interpreter can fail to reload
    # Tcl library files. A fresh process also resets CTk's global callbacks.
    for check in checks:
        print("Native GUI check: " + check, flush=True)
        pytest("-q", check)


if __name__ == "__main__":
    main()
