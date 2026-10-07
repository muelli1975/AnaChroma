# AnaChroma – Development builds

The current implementation is **0.1.0.dev3**, not a v1 release. The current build creates an unpack-and-run directory for the platform on which it is executed. It includes Python/Tk, Pillow, NumPy, CustomTkinter and the shared sound; it bundles the separately built CIELab PNG executable, matching complete sources and licenses. The official ExifTool distribution is bundled with its support files, licenses and sources; Linux/macOS require system Perl.

## Build locally

Use Python 3.12 with Tcl/Tk and a fresh environment. From the repository root:

```sh
python -m venv .venv
# Activate .venv.
python -m pip install -r requirements-build.txt -e .
python scripts/build_cielab.py  # Requires a C compiler; downloads hash-verified PNG dependencies.
python scripts/prepare_exiftool.py  # Downloads hash-verified official ExifTool distributions.
python -m pytest -q
python scripts/build.py
python scripts/smoke_cielab.py dist/AnaChroma/tools/cielab
python scripts/smoke_build.py  # Linux: run this check under xvfb-run if needed.
```

The output is `dist/AnaChroma`. Run `AnaChroma.exe` on Windows or `./AnaChroma` on Linux/macOS inside that folder. Keep `_internal` beside the executable. macOS packaging is currently a portable directory rather than a signed/notarized installer; PyInstaller also creates an app bundle locally, but the workflow archives the directory.

`BUILD_INFO.json` records interpreter, platform, source commit and library versions. Primary build inputs are pinned; this is not a claim of byte-identical packages across machines. Source installs support Python 3.10+, while the pinned development build dependencies target Python 3.12.

## CI packages

`.github/workflows/build.yml` tests and builds on Ubuntu 24.04, Windows Server 2022 and macOS 14. The Linux job installs FFmpeg, ExifTool and Xvfb **for validation**, including the real Batch-filter and GUI tests. Missing optional reference tools and an unavailable display are reported as test skips elsewhere. FFmpeg is never a production processing dependency.

Packages are downloadable as GitHub Actions artifacts after a successful run, retained for 14 days. Linux/macOS use a tar archive to preserve executable permissions; Windows uses ZIP. These are development artifacts, not published releases. The actions themselves are pinned by commit. After building, the workflow launches the actual packaged GUI with the bundled SBS example, checks the native CIELab executable including Unicode paths, and requires normal shutdown before uploading an artifact. Windows additionally compares lossless PNG pixels against the actual CIELab executable from AnaglyphBatch 1.0; a difference above 2/255 stops the job and produces a report artifact for investigation.

Native macOS Intel builds and final release publication are not configured yet. Native desktop checks and a decision on each platform's external tool distribution remain necessary before a release.

## External tools

Place complete, licensed distributions under `tools` beside the executable, or install them on PATH:

| Platform | ExifTool | CIELab |
| --- | --- | --- |
| Windows | `tools/exiftool.exe` with its original companion files | bundled `tools/cielab/cielab.exe`, matching sources and licenses |
| Linux/macOS | bundled `tools/exiftool` and Perl modules; a working system Perl interpreter is required | bundled executable `tools/cielab/cielab`, matching sources and licenses |

The adapter uses `cielab left.png right.png -o output.png`, with separate already resized halves and an isolated temporary directory. The native PNG port keeps the original CIELab math and levmar solver byte-for-byte. It replaces the obsolete OpenCV front end with statically linked libpng/zlib. See `native/cielab/README.md` for source provenance, licensing and rebuilding offline from the included source archive. The executable itself does not resize images.

ExifTool's time limit is 30 seconds per export; CIELab's is 600 seconds per calculation. Cancellation terminates the directly launched process, then kills it if necessary. Metadata failures keep the finished JPEG and produce a warning.

## Distribution material

The build copies both READMEs, the project license, third-party notices and installed runtime libraries' license material. Review that material and the recorded manifest for the actual target build. Complete external tool licenses and any additional native dependency notices must accompany those distributions if later bundled. The application works offline after installation/unpacking.
