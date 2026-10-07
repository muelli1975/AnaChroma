"""Exercise the actual native executable, including paths with Unicode/spaces."""
from pathlib import Path
import subprocess
import sys
import tempfile
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parents[1]
directory = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "tools" / "cielab"
executable = (directory / ("cielab.exe" if sys.platform == "win32" else "cielab")).resolve()
with tempfile.TemporaryDirectory(prefix="AnaChroma ä Ω ") as folder:
    path = Path(folder)
    left = np.random.default_rng(1975).integers(0, 256, (8, 16, 3), dtype=np.uint8)
    right = np.random.default_rng(2026).integers(0, 256, (8, 16, 3), dtype=np.uint8)
    Image.fromarray(left).save(path / "links ä.png")
    Image.fromarray(right).save(path / "rechts Ω.png")
    subprocess.run([str(executable), str(path / "links ä.png"), str(path / "rechts Ω.png"),
                    "-o", str(path / "ausgabe.png")], check=True, timeout=30)
    with Image.open(path / "ausgabe.png") as output:
        assert output.mode == "RGB" and output.size == (16, 8)
        assert np.ptp(np.asarray(output)) > 0
    # Both input halves must have equal dimensions.
    Image.new("RGB", (4, 4)).save(path / "klein.png")
    mismatch = subprocess.run([str(executable), str(path / "klein.png"), str(path / "rechts Ω.png"),
                               "-o", str(path / "fehler.png")], capture_output=True, timeout=30)
    assert mismatch.returncode and not (path / "fehler.png").exists()
print("Native CIELab: real RGB8 computation, Unicode paths and dimension validation passed.")
