# AnaChroma

[Deutsch](README_DE.md)

**High-quality anaglyphs from SBS images**

AnaChroma is a compact local desktop tool being developed to convert Full-SBS stereoscopic images into high-quality anaglyphs. It builds on the proven processing methods of [AnaglyphBatch](https://github.com/muelli1975/AnaglyphBatch), adding automatic preview, image navigation and convenient single-image and folder processing.

The application is designed to work completely locally: no account, no cloud, no tracking and no online dependencies during use.

## Development status

The first runnable development version is **0.1.0.dev1**. The German desktop interface, shared processing engine, custom preset editor and single-image/folder export are implemented. This is a development build, not a version 1 release. Your supplied AnaChroma icon is integrated. Native CIELab builds are still pending; real stereoscopic photographs and native Windows/macOS use still need practical validation.

GitHub Actions prepares development packages for Windows, Linux and macOS. Successful packaging alone does not establish image quality or native desktop compatibility. See [build instructions](docs/BUILD.md) and [validation](docs/VALIDATION.md).

## Workflow

1. Open an SBS image or select an image folder.
2. Browse the images and choose an anaglyph method; the preview updates automatically.
3. Select the output folder and image size.
4. Choose **Save current image** or **Process all**.

Opening a single image also makes the other supported images in the same folder available for navigation. Optional recursive folder processing preserves the input folder structure in the output.

## Supported input

AnaChroma accepts parallel Full-SBS images in JPEG/JPG, PNG, TIFF/TIF, BMP and WebP format. The left view is on the left and the right view is on the right. Both views must have their full width; Half-SBS decompression is outside the current scope.

EXIF orientation is applied when loading. The oriented image must have an even width so it can be divided into two equal views.

## Anaglyph methods and preview

The current AnaglyphBatch provides 18 methods, including Dubois LCD with red-channel correction, Dubois, Compromise, Wimmer, Cosima 3/4, Rendepth 1/2, iaian7, Color, Half-Color, Grey, Oldschool, Frans van den Poel, John Wattie, Dubois green/magenta, Dubois amber/blue and external CIELab Least Squares.

One method is selected at a time. Methods retain their individual processing rules; sRGB linearization is used only where required by the reference pipeline. Preview and export share the same processing core. Automatic preview is limited to a maximum long edge of 1024 px.

An explicit **Create custom method…** action opens the preset editor. Two 3 × 3 matrices can be adjusted through numeric fields, sliders and the mouse wheel, with a dedicated live preview. Matrix sliders start at −2 to +2 with 0.001 steps; direct numeric entry preserves finer coefficients and extends the slider when necessary. This is a practical editing range, not a physical limit for anaglyphs. Custom presets also include an optional linear-light calculation, brightness/contrast adjustment and individual RGB correction values. Settings appear directly beneath the matrices and are stored locally; built-in methods retain their reference behavior.

## Output

The standard output is **JPEG quality 90, 4:4:4 without chroma subsampling, with optimized JPEG coding**. A separate **JPEG quality 95 for print/archive** option is available. Resizing uses Lanczos interpolation and preserves the aspect ratio.

Available sizes:

- Original
- 1080p: fit within 1920 × 1080 px
- 2160p: fit within 3840 × 2160 px
- 2048 px long edge
- Custom long or short edge

Output filenames use the current AnaglyphBatch suffixes, such as `image_dubois_lcd.jpg` or `image_compromise.jpg`.

Metadata is copied using ExifTool where possible, excluding embedded original previews, thumbnails and orientation tags. A metadata failure will be reported without discarding a successfully written image.

## Scope

AnaChroma focuses on SBS-to-anaglyph conversion. Stereo alignment and correction remain the purpose of [StereoFine](https://github.com/muelli1975/StereoFine); 2D-to-3D conversion remains the purpose of [SplatTricia](https://github.com/muelli1975/SplatTricia).

Version 1 does not include separate left/right pair detection, MPO splitting, stereo-window correction, a thumbnail gallery, high-bit-depth output or video processing. Dedicated ghosting compensation requires a separately validated method and is not yet part of the agreed implementation.

## Source and builds

The core uses Python, Pillow and NumPy, with CustomTkinter for the interface. The existing sRGB transfer module from SplatTricia is reused unchanged. FFmpeg is not required as the normal processing engine.

The build script creates a portable directory on the current platform. ExifTool and CIELab are external components and are not bundled in these first development packages. Platform-specific CIELab builds must be verified before their availability is promised in a release.

The agreed scope is documented in [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md), the module structure in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and the source baseline in [docs/REFERENCE_BASELINE.md](docs/REFERENCE_BASELINE.md).

## Run from source

Use Python 3.10 or newer with Tcl/Tk installed (development packages use Python 3.12). From the repository directory:

```sh
python -m venv .venv
# Activate .venv using your platform's usual command.
python -m pip install -e .
python run_anachroma.py
```

On Windows activate with `.venv\Scripts\activate`; on Linux/macOS use `source .venv/bin/activate`. Some Linux Python distributions require their separate Tk package.

ExifTool is found in `tools/exiftool.exe` (Windows), `tools/exiftool` or the system PATH. The Windows ExifTool distribution's companion files must remain beside its executable. CIELab is found in `tools/cielab/cielab.exe`, `tools/cielab/cielab` or PATH. Without ExifTool, export succeeds with a metadata warning; without CIELab, the other 17 methods remain usable.

The default output is `output` beside the program/source checkout. Paths and the recursive option are remembered in `settings.json`; custom methods are saved in `presets.json`. A read-only program folder uses the user's configuration folder. Existing outputs with the same name are replaced only after a complete new image has been written; conflicting input names are rejected.

Read [custom presets](docs/PRESET_EDITOR.md) for coefficient orientation, linearization and channel corrections. The editor does not infer whether a copied web matrix requires linear RGB; use its source's processing instructions.

## License

AnaChroma source code and original documentation created by Christoph Müller are released under the **MIT License**. Third-party components remain under their respective licenses.

See [LICENSE.txt](LICENSE.txt) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
