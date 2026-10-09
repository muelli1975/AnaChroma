# AnaChroma 1.0

[Deutsch](README_DE.md)

**High-quality anaglyphs from SBS images**

AnaChroma converts Full-SBS stereo images into high-quality anaglyphs with automatic preview, image navigation and single-image or folder export. It works completely locally, without an account, cloud or tracking.

## Quick start

1. Open a single image or an image folder. Opening a single image also enables navigation through neighbouring images.
2. Choose an anaglyph method and inspect the preview.
3. Choose the output folder and image size. Under **Output methods**, optionally select several methods for simultaneous export.
4. Use **Save image** or **Process all**. Folder processing can include subfolders.

JPEG/JPG, PNG, TIFF/TIF, BMP and WebP are supported. Full-SBS means two views at full width, left eye on the left and right eye on the right. EXIF orientation is applied before splitting; the oriented image must have an even width.

## Methods and preview

18 methods include Dubois LCD with red correction, Dubois, Compromise, Wimmer, Cosima, Rendepth, iaian7, Grey, Color, green/magenta, amber/blue and CIELab Least Squares. Preview and export use the same processing rules.

The automatic preview follows the available window area, up to a 1600 px long edge; CIELab uses up to 1024 px. Both fill the same display area. A black surround keeps existing floating stereo windows visible. The original 7680 × 2160 SBS example image is included.

**Create custom method…**, beneath the standard methods in the menu, opens a compact editor. Adjust two 3 × 3 matrices with exact numeric entry, sliders and the mouse wheel. Optional linear-light calculation and RGB colour correction are available. Changes appear in the main preview; save a preset to reuse it. The [editor guide](docs/PRESET_EDITOR.md) explains coefficients and correction values.

Shortcuts: **Left/Right** or **Page Up/Page Down** browse images; **Ctrl+Left/Right** switch preview methods. Text fields and selected sliders retain their usual controls.

## Output

JPEG quality **90**, **4:4:4** without chroma subsampling, with optimized coding. Optional **JPEG quality 95 for print/archive**. Lanczos resizing preserves the aspect ratio.

Sizes: Original; 1080p (within 1920 × 1080); 2160p (within 3840 × 2160); 2048 px long edge; custom long or short edge.

**Use subfolder in program folder** selects `output` beside the program. **Choose** selects a custom output folder. **Output destination** shows the active path. Folder processing preserves the source root name and relative subfolders under either destination. Each selected method gets its filename suffix, for example `image_dubois_lcd.jpg`. Existing results are replaced only after a complete new file has been written; colliding names and original overwrites are rejected before export.

ExifTool copies metadata while excluding original previews, thumbnails and orientation. A metadata warning keeps the exported image. Progress counts actual output files; processing can be cancelled.

## Portable builds and source

Extract the complete [release package](https://github.com/muelli1975/AnaChroma/releases) and start AnaChroma. Keep the supplied application files and tools together. Windows includes the required runtimes; Linux/macOS need Tcl/Tk for source use and system Perl for ExifTool. macOS builds are ad-hoc signed and not notarized.

Settings and custom methods stay local in `settings.json` and `presets.json` beside the program, with a user configuration folder fallback if the program folder is read-only. Paths, output mode, language and recursive selection are remembered.

The core uses Python, Pillow and NumPy with CustomTkinter. CIELab and ExifTool are bundled as separate tools with their licenses and corresponding sources. Release packages include a `source` folder for the matching application source. Build details: [BUILD.md](docs/BUILD.md).

To run from source, use Python 3.10+ with Tcl/Tk:

```sh
python -m venv .venv
# Activate .venv for your platform.
python -m pip install -e .
python run_anachroma.py
```

## License

Copyright Christoph Müller. MIT License for AnaChroma; bundled third-party components retain their own licenses. See [LICENSE.txt](LICENSE.txt) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
