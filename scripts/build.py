"""Build an unpack-and-run directory on the current platform, without tools."""
from __future__ import annotations
import importlib.metadata as metadata
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    import PyInstaller.__main__
    arguments = [str(ROOT / "run_anachroma.py"), "--name=AnaChroma", "--onedir",
                 "--windowed", "--clean", "--noconfirm", "--noupx",
                 f"--paths={ROOT / 'src'}", "--collect-all=customtkinter",
                 "--hidden-import=PIL._tkinter_finder",
                 f"--add-data={ROOT / 'assets'}:assets",
                 f"--distpath={ROOT / 'dist'}", f"--workpath={ROOT / 'build'}",
                 f"--specpath={ROOT / 'build'}"]
    # PyInstaller converts ICO to ICNS for the optional macOS app bundle.
    icon = ROOT / "assets" / "anachroma.ico"
    if sys.platform in {"win32", "darwin"} and icon.is_file():
        arguments.append(f"--icon={icon}")
    # Some Python distributions keep Tcl/Tk outside the system linker paths.
    # Supplying those libraries explicitly avoids a successful-looking build
    # that fails on startup because PyInstaller could not resolve them.
    if sys.platform == "linux":
        library_dir = Path(sys.base_prefix) / "lib"
        libraries = set(library_dir.glob("libtcl*.so*")) | set(library_dir.glob("libtk*.so*"))
        for library in sorted(libraries):
            arguments.append(f"--add-binary={library}:.")
    PyInstaller.__main__.run(arguments)
    portable = ROOT / "dist" / "AnaChroma"
    for filename in ("README.md", "README_DE.md", "LICENSE.txt", "THIRD_PARTY_NOTICES.md"):
        shutil.copy2(ROOT / filename, portable / filename)
    licenses = portable / "licenses"
    licenses.mkdir(exist_ok=True)
    shutil.copytree(ROOT / "licenses", licenses, dirs_exist_ok=True)
    # Collect shipped libraries' own license material, including transitive
    # runtime dependencies. Build-only tools are recorded but not relabeled.
    runtime = ("numpy", "Pillow", "customtkinter", "darkdetect", "packaging")
    for name in runtime + ("pyinstaller",):
        distribution = metadata.distribution(name)
        for path in distribution.files or ():
            parts = [part.lower() for part in path.parts]
            if any(part.startswith(("license", "copying", "notice", "copyright")) for part in parts):
                source = Path(distribution.locate_file(path))
                if source.is_file():
                    destination = licenses / name / Path(*[p for p in path.parts if p not in ("..", ".")])
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
    # Python runtime; Tcl/Tk and font license terms are supplied in licenses/.
    for source in (Path(sys.base_prefix) / "LICENSE.txt", Path(sys.base_prefix) / "LICENSE",
                   Path(sys.base_prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "LICENSE.txt"):
        if source.is_file():
            shutil.copy2(source, licenses / "Python-LICENSE.txt")
            break
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "unknown"
    manifest = {"python": sys.version, "platform": sys.platform, "commit": commit,
                "dependencies": {name: metadata.version(name) for name in runtime + ("pyinstaller", "pyinstaller-hooks-contrib")},
                "external_tools_bundled": False}
    (portable / "BUILD_INFO.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Portable development build: {portable}")


if __name__ == "__main__":
    main()
