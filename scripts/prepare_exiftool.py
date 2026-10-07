"""Bundle a pinned official ExifTool distribution, including all support files."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tarfile
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "13.59"
SOURCE = ("Image-ExifTool-13.59.tar.gz", "668ea3acececb7235fbd0f4900e72d5f12c9b07e5c778fd36cb1e9b5828fd65a")
WINDOWS = ("exiftool-13.59_64.zip", "44b512b25af500724ba579d0a53c8fc5851628b692dd5e5d94ae4a15c2cba9ec")


def download(name, digest):
    cache = ROOT / "build" / "exiftool-download"
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / name
    if not path.is_file():
        url = "https://downloads.sourceforge.net/project/exiftool/" + name
        with urllib.request.urlopen(url, timeout=60) as response:
            path.write_bytes(response.read())
    if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        path.unlink()
        raise RuntimeError("ExifTool download does not match the official SHA-256: " + name)
    return path


def main():
    source = download(*SOURCE)
    staging = ROOT / "build" / "exiftool-staging"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    with tarfile.open(source) as archive:
        archive.extractall(staging, filter="data")
    distribution = staging / ("Image-ExifTool-" + VERSION)
    tools = ROOT / "tools"
    tools.mkdir(exist_ok=True)
    if sys.platform == "win32":
        binary = download(*WINDOWS)
        with zipfile.ZipFile(binary) as archive:
            for member in archive.infolist():
                if ".." in Path(member.filename).parts or Path(member.filename).is_absolute():
                    raise RuntimeError("Invalid archive member")
            archive.extractall(staging)
        windows = staging / ("exiftool-" + VERSION + "_64")
        shutil.copy2(windows / "exiftool(-k).exe", tools / "exiftool.exe")
        shutil.copytree(windows / "exiftool_files", tools / "exiftool_files", dirs_exist_ok=True)
        for path in windows.iterdir():
            if path.is_file() and path.suffix.lower() != ".exe":
                shutil.copy2(path, tools / path.name)
    else:
        shutil.copy2(distribution / "exiftool", tools / "exiftool")
        (tools / "exiftool").chmod(0o755)
        shutil.copytree(distribution / "lib", tools / "lib", dirs_exist_ok=True)
    notices = tools / "exiftool-distribution"
    notices.mkdir(exist_ok=True)
    for name in ("README", "Changes", "Artistic", "Copying"):
        if (distribution / name).is_file():
            shutil.copy2(distribution / name, notices / name)
    shutil.copy2(source, notices / SOURCE[0])
    manifest = {"version": VERSION, "source_sha256": SOURCE[1],
                "windows_sha256": WINDOWS[1] if sys.platform == "win32" else None,
                "checksums_url": "https://exiftool.org/checksums-13.59.txt",
                "requires_system_perl": sys.platform != "win32"}
    (notices / "BUILD_INFO.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    print("Prepared official ExifTool " + VERSION + " with original support files and license/source distribution.")


if __name__ == "__main__":
    main()
