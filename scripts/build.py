"""Build an unpack-and-run directory, including a prepared native CIELab tool."""
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
    native = ROOT / "tools" / "cielab"
    native_name = "cielab.exe" if sys.platform == "win32" else "cielab"
    if not (native / native_name).is_file() or not (native / "cielab-source.tar.gz").is_file():
        raise RuntimeError("Run python scripts/build_cielab.py before packaging.")
    shutil.copytree(native, portable / "tools" / "cielab", dirs_exist_ok=True)
    exif_name = "exiftool.exe" if sys.platform == "win32" else "exiftool"
    if not (ROOT / "tools" / exif_name).is_file() or not (ROOT / "tools" / "exiftool-distribution" / "BUILD_INFO.json").is_file():
        raise RuntimeError("Run python scripts/prepare_exiftool.py before packaging.")
    for path in (ROOT / "tools").iterdir():
        if path.name == "cielab":
            continue
        if path.is_dir():
            shutil.copytree(path, portable / "tools" / path.name, dirs_exist_ok=True)
        else:
            shutil.copy2(path, portable / "tools" / path.name)
    # The optional macOS .app uses its own resource directory.
    mac_resources = ROOT / "dist" / "AnaChroma.app" / "Contents" / "Resources"
    if sys.platform == "darwin" and mac_resources.is_dir():
        shutil.copytree(ROOT / "tools", mac_resources / "tools", dirs_exist_ok=True)
    for filename in ("README.md", "README_DE.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "RELEASE_NOTES_1.0.md"):
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
                "external_tools_bundled": {"cielab": True, "exiftool": True},
                "exiftool": json.loads((ROOT / "tools" / "exiftool-distribution" / "BUILD_INFO.json").read_text()),
                "cielab": json.loads((native / "BUILD_INFO.json").read_text())}
    (portable / "BUILD_INFO.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    from release_support import prepare
    allowed = {"src", "scripts", "native", "assets", "docs", "tests", "licenses",
               "run_anachroma.py", "pyproject.toml", "requirements-build.txt", "requirements-runtime.txt",
               "README.md", "README_DE.md", "LICENSE", "THIRD_PARTY_NOTICES.md",
               "RELEASE_NOTES_1.0.md", "DESIGN_STANDARD_STEREOTOOLS.txt", "AGENTS.md"}
    prepare(ROOT, portable, allowed)
    if sys.platform == "darwin":
        bundle = ROOT / "dist" / "AnaChroma.app"
        subprocess.run(["codesign", "--force", "--deep", "--sign", "-", str(bundle)], check=True)
        subprocess.run(["codesign", "--verify", "--deep", "--strict", str(bundle)], check=True)
    print(f"Portable build: {portable}")


if __name__ == "__main__":
    main()
