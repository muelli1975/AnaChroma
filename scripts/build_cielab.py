"""Build the GPL CIELab executable and bundle its complete matching sources."""
from __future__ import annotations
import hashlib
import json
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "native" / "cielab"


def main():
    info = json.loads((SOURCE / "SOURCES.json").read_text())
    for name, expected in info["files"].items():
        actual = hashlib.sha256((SOURCE / "upstream" / name).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Upstream file changed: {name}")
    work = ROOT / "build" / "cielab"
    deps = work / "sources"
    deps.mkdir(parents=True, exist_ok=True)
    for dependency in info["dependencies"]:
        name, version = dependency["name"], dependency["version"]
        archive = deps / f"{name}-{version}.tar.gz"
        if not archive.is_file():
            with urllib.request.urlopen(dependency["url"], timeout=90) as response:
                data = response.read()
            archive.write_bytes(data)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != dependency["sha256"]:
            raise RuntimeError(f"Source archive hash mismatch: {archive}")
        directory = deps / f"{name}-{version}"
        if not directory.is_dir():
            with tarfile.open(archive) as source:
                # Source archives are pinned and verified above. Also reject
                # path traversal and links before extracting on all Pythons.
                for member in source.getmembers():
                    target = (deps / member.name).resolve()
                    if not target.is_relative_to(deps.resolve()) or member.issym() or member.islnk():
                        raise RuntimeError(f"Unsafe archive member: {member.name}")
                source.extractall(deps, filter="data")
    cmake = shutil.which("cmake")
    if not cmake:
        # pip-installed cmake in a venv also works when called without activation.
        candidate = Path(sys.executable).parent / ("cmake.exe" if sys.platform == "win32" else "cmake")
        cmake = str(candidate) if candidate.is_file() else None
    if not cmake:
        raise RuntimeError("Install the pinned build requirements (CMake required).")
    out = ROOT / "tools" / "cielab"
    commands = ([cmake, "-S", str(SOURCE), "-B", str(work / "objects"),
                 "-DCMAKE_BUILD_TYPE=Release", f"-DCIELAB_DEPS={deps.resolve()}"],
                [cmake, "--build", str(work / "objects"), "--config", "Release", "--parallel", "2", "--target", "cielab"],
                [cmake, "--install", str(work / "objects"), "--config", "Release", "--component", "CIELab", "--prefix", str(out)])
    for command in commands:
        subprocess.run(command, check=True)
    shutil.copy2(SOURCE / "upstream" / "LICENSE.txt", out / "LICENSE-GPL-3.txt")
    shutil.copy2(SOURCE / "upstream" / "levmar" / "LICENSE", out / "LICENSE-levmar.txt")
    shutil.copy2(deps / "libpng-1.6.59" / "LICENSE", out / "LICENSE-libpng.txt")
    shutil.copy2(deps / "zlib-1.3.2" / "LICENSE", out / "LICENSE-zlib.txt")
    # Bundled source archive can rebuild offline: -DCIELAB_DEPS=<sources/dependencies>.
    with tarfile.open(out / "cielab-source.tar.gz", "w:gz") as archive:
        archive.add(SOURCE, arcname="cielab-source/native")
        archive.add(Path(__file__), arcname="cielab-source/build_cielab.py")
        archive.add(ROOT / "LICENSE", arcname="cielab-source/AnaChroma-MIT-LICENSE.txt")
        for dependency in info["dependencies"]:
            name = f"{dependency['name']}-{dependency['version']}"
            archive.add(deps / name, arcname=f"cielab-source/dependencies/{name}")
    executable = out / ("cielab.exe" if sys.platform == "win32" else "cielab")
    info["platform"] = sys.platform
    info["architecture"] = platform.machine()
    info["floating_point"] = "precise; no fast-math or fused contraction"
    info["binary_sha256"] = hashlib.sha256(executable.read_bytes()).hexdigest()
    (out / "BUILD_INFO.json").write_text(json.dumps(info, indent=2) + "\n")
    shutil.copy2(SOURCE / "README.md", out / "README.md")
    print(f"Native CIELab executable and corresponding sources: {out}")


if __name__ == "__main__":
    main()
