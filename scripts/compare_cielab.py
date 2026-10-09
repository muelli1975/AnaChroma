"""Windows: compare lossless pixels with the actual Batch 1.0 executable."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import urllib.request
import zipfile
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
URL = "https://github.com/muelli1975/AnaglyphBatch/releases/download/1.0/AnaglyphBatch_1.0.zip"
HASH = "2f192dbf7f36c152cf7b35566aefc84058844e28b6a548fd3752f8488a708286"


def main():
    if sys.platform != "win32":
        raise RuntimeError("The original executable requires Windows.")
    work = ROOT / "build" / "cielab-comparison"
    work.mkdir(parents=True, exist_ok=True)
    archive = work / "batch-reference.zip"
    with urllib.request.urlopen(URL, timeout=120) as response:
        archive.write_bytes(response.read())
    if hashlib.sha256(archive.read_bytes()).hexdigest() != HASH:
        raise RuntimeError("Batch reference ZIP changed.")
    old = work / "old"
    old.mkdir(exist_ok=True)
    with zipfile.ZipFile(archive) as zipped:
        for name in zipped.namelist():
            if name.startswith("AnaglyphBatch/tools/cielab/") and not name.endswith("/"):
                (old / Path(name).name).write_bytes(zipped.read(name))
    archive.unlink()  # Do not include the complete unrelated tools distribution.
    current = ROOT / "tools" / "cielab" / "cielab.exe"
    rng = np.random.default_rng(1975)
    cases = {"random": (rng.integers(0, 256, (32, 32, 3), dtype=np.uint8),
                        rng.integers(0, 256, (32, 32, 3), dtype=np.uint8))}
    ramp = np.repeat(np.arange(256, dtype=np.uint8)[None, :, None], 3, axis=2)
    cases["gray"] = (ramp, ramp.copy())
    colors = np.array([[r, g, b] for r in (0, 64, 128, 192, 255)
                       for g in (0, 64, 128, 192, 255) for b in (0, 64, 128, 192, 255)], dtype=np.uint8)[None]
    cases["colors"] = (colors, colors[:, ::-1].copy())
    with Image.open(ROOT / "assets" / "anachroma.jpg") as sbs:
        left = sbs.crop((0, 0, sbs.width // 2, sbs.height)).resize((128, 72), Image.Resampling.LANCZOS)
        right = sbs.crop((sbs.width // 2, 0, sbs.width, sbs.height)).resize((128, 72), Image.Resampling.LANCZOS)
        cases["demo"] = (np.asarray(left), np.asarray(right))
    results = []
    for name, (left, right) in cases.items():
        l, r = work / f"{name}-left.png", work / f"{name}-right.png"
        Image.fromarray(left).save(l); Image.fromarray(right).save(r)
        outputs = []
        for label, tool in (("reference", old / "cielab.exe"), ("new", current)):
            target = work / f"{name}-{label}.png"
            subprocess.run([str(tool), str(l), str(r), "-o", str(target)], check=True, timeout=180)
            with Image.open(target) as image:
                outputs.append(np.asarray(image.convert("RGB")).astype(np.int16))
        difference = np.abs(outputs[0] - outputs[1])
        results.append({"case": name, "pixels": int(left.shape[0] * left.shape[1]),
                        "max_channel_difference": int(difference.max()),
                        "mean_channel_difference": float(difference.mean()),
                        "changed_pixels": int(np.any(difference, axis=2).sum())})
    report = {"reference": URL, "reference_archive_sha256": HASH, "results": results}
    (work / "comparison.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    # A verification threshold, not a claim about perceptual equivalence.
    if any(result["max_channel_difference"] > 2 for result in results):
        raise RuntimeError("CIELab differs by more than 2/255: review before distribution/replacing Batch.")


if __name__ == "__main__":
    main()
