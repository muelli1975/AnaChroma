# AnaChroma – Development builds

The first implementation is **0.1.0.dev1**, not a v1 release. The current build creates an unpack-and-run directory for the platform on which it is executed. It includes Python/Tk, Pillow, NumPy, CustomTkinter and the shared sound; it does not download or bundle ExifTool or CIELab.

## Build locally

Use Python 3.12 with Tcl/Tk and a fresh environment. From the repository root:

```sh
python -m venv .venv
# Activate .venv.
python -m pip install -r requirements-build.txt -e .
python -m pytest -q
python scripts/build.py
```

The output is `dist/AnaChroma`. Run `AnaChroma.exe` on Windows or `./AnaChroma` on Linux/macOS inside that folder. Keep `_internal` beside the executable. macOS packaging is currently a portable directory rather than a signed/notarized installer; PyInstaller also creates an app bundle locally, but the workflow archives the directory.

`BUILD_INFO.json` records interpreter, platform, source commit and library versions. Primary build inputs are pinned; this is not a claim of byte-identical packages across machines. Source installs support Python 3.10+, while the pinned development build dependencies target Python 3.12.

## CI packages

`.github/workflows/build.yml` tests and builds on Ubuntu 24.04, Windows Server 2022 and macOS 14. The Linux job installs FFmpeg, ExifTool and Xvfb **for validation**, including the real Batch-filter and GUI tests. Missing optional reference tools and an unavailable display are reported as test skips elsewhere. FFmpeg is never a production processing dependency.

Packages are downloadable as GitHub Actions artifacts after a successful run, retained for 14 days. Linux/macOS use a tar archive to preserve executable permissions; Windows uses ZIP. These are development artifacts, not published releases. The actions themselves are pinned by commit.

Native macOS Intel builds and final release publication are not configured yet. Native desktop checks and a decision on each platform's external tool distribution remain necessary before a release.

## External tools

Place complete, licensed distributions under `tools` beside the executable, or install them on PATH:

| Platform | ExifTool | CIELab |
| --- | --- | --- |
| Windows | `tools/exiftool.exe` with its original companion files | `tools/cielab/cielab.exe` with required DLLs |
| Linux/macOS | executable `tools/exiftool` and its Perl distribution/runtime, or PATH installation | executable `tools/cielab/cielab` with required shared libraries, or PATH installation |

The adapter uses `cielab left.png right.png -o output.png`, with separate already resized halves and an isolated temporary directory. Recompilation against modern OpenCV/levmar and verification on all target platforms remain separate work. No untested binary is supplied by this build script.

ExifTool's time limit is 30 seconds per export; CIELab's is 600 seconds per calculation. Cancellation terminates the directly launched process, then kills it if necessary. Metadata failures keep the finished JPEG and produce a warning.

## Distribution material

The build copies both READMEs, the project license, third-party notices and installed runtime libraries' license material. Review that material and the recorded manifest for the actual target build. Complete external tool licenses and any additional native dependency notices must accompany those distributions if later bundled. The application works offline after installation/unpacking.
