"""Archive the complete native tool separately for use with AnaglyphBatch."""
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parents[1]
output = root / "dist"
output.mkdir(exist_ok=True)
platform = sys.argv[1] if len(sys.argv) > 1 else sys.platform
kind = "zip" if sys.platform == "win32" else "gztar"
path = shutil.make_archive(str(output / f"CIELab-{platform}"), kind,
                           root_dir=root / "tools", base_dir="cielab")
print(path)
