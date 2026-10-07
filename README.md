# AnaChroma

[Deutsch](README_DE.md)

**High-quality anaglyphs from SBS images**

AnaChroma is a compact local desktop tool being developed to convert Full-SBS stereoscopic images into high-quality anaglyphs. It builds on the proven processing methods of [AnaglyphBatch](https://github.com/muelli1975/AnaglyphBatch), adding automatic preview, image navigation and convenient single-image and folder processing.

The application is designed to work completely locally: no account, no cloud, no tracking and no online dependencies during use.

## Development status

AnaChroma is in early development. This repository currently contains the project specification, technical reference notes and the shared completion sound. A runnable application and downloadable releases are not yet available. The features below describe the agreed scope for version 1.

## Planned workflow

1. Open an SBS image or select an image folder.
2. Browse the images and choose an anaglyph method; the preview updates automatically.
3. Select the output folder and image size.
4. Choose **Save current image** or **Process all**.

Opening a single image also makes the other supported images in the same folder available for navigation. Optional recursive folder processing preserves the input folder structure in the output.

## Supported input

Version 1 is planned for parallel Full-SBS images in JPEG/JPG, PNG, TIFF/TIF, BMP and WebP format. The left view is on the left and the right view is on the right. Both views must have their full width; Half-SBS decompression is outside the current scope.

EXIF orientation is applied when loading. The oriented image must have an even width so it can be divided into two equal views.

## Anaglyph methods and preview

The current AnaglyphBatch provides 18 methods, including Dubois LCD with red-channel correction, Dubois, Compromise, Wimmer, Cosima 3/4, Rendepth 1/2, iaian7, Color, Half-Color, Grey, Oldschool, Frans van den Poel, John Wattie, Dubois green/magenta, Dubois amber/blue and external CIELab Least Squares.

One method is selected at a time. Methods retain their individual processing rules; sRGB linearization is used only where required by the reference pipeline. Preview and export share the same processing core. Automatic preview is limited to a maximum long edge of 1024 px.

## Output

The standard output is **JPEG quality 90, 4:4:4 without chroma subsampling, with optimized JPEG coding**. A separate **JPEG quality 95 for print/archive** option is planned. Resizing uses Lanczos interpolation and preserves the aspect ratio.

Planned sizes:

- Original
- 1080p: fit within 1920 × 1080 px
- 2160p: fit within 3840 × 2160 px
- 2048 px long edge
- Custom long or short edge

Output filenames use the current AnaglyphBatch suffixes, such as `image_dubois_lcd.jpg` or `image_compromise.jpg`.

Metadata is copied using ExifTool where possible, excluding embedded original previews, thumbnails and orientation tags. A metadata failure will be reported without discarding a successfully written image.

## Scope

AnaChroma focuses on SBS-to-anaglyph conversion. Stereo alignment and correction remain the purpose of [StereoFine](https://github.com/muelli1975/StereoFine); 2D-to-3D conversion remains the purpose of [SplatTricia](https://github.com/muelli1975/SplatTricia).

Version 1 does not include separate left/right pair detection, MPO splitting, stereo-window correction, a matrix editor, a thumbnail gallery, high-bit-depth output or video processing.

## Source and builds

The planned core uses Python, Pillow and NumPy, with CustomTkinter for the interface. The existing sRGB transfer module from SplatTricia is reused. FFmpeg is not required as the normal processing engine.

Portable builds are intended for Windows, Linux and macOS. ExifTool and CIELab are external components. Platform-specific CIELab builds must be verified before their availability is promised in a release.

The agreed scope is documented in [docs/PROJECT_SPEC.md](docs/PROJECT_SPEC.md), the intended structure in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), and the source baseline in [docs/REFERENCE_BASELINE.md](docs/REFERENCE_BASELINE.md).

## License

AnaChroma source code and original documentation created by Christoph Müller are released under the **MIT License**. Third-party components remain under their respective licenses.

See [LICENSE.txt](LICENSE.txt) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
