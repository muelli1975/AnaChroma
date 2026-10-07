"""Start the actual built GUI, render an image and require normal shutdown."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
name = "AnaChroma.exe" if sys.platform == "win32" else "AnaChroma"
executable = root / "dist" / "AnaChroma" / name
subprocess.run([str(executable), "--smoke-test"], check=True, timeout=60)
print("Portable GUI displayed the bundled SBS, calculated CIELab, exported JPEG with ExifTool metadata and closed successfully.")
