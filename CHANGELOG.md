# Changelog

## Unreleased

- Establish the AnaChroma project scope and source baseline.
- Add English and German READMEs in the shared Stereo-Tool style.
- Record the current 18 AnaglyphBatch methods and their filename suffixes.
- Document reuse of the existing sRGB transfer module and the CIELab scaling exception.
- Add the unchanged shared completion sound and its SHA-256 hash.
- Retain the project's MIT License and distinguish planned third-party components.
- Extend the agreed v1 scope with custom presets, optional linear-light calculation, brightness/contrast and RGB correction values.
- Specify a visible custom-method action and numeric matrix controls with sliders, focused mouse-wheel adjustment and continuous preview.
- Remove unsupported provisional control ranges and modifier steps; record SPM and Cosima evidence and require parameter-specific formulas and justified limits before implementation.

## 0.1.0.dev1 — 2026-10-07

First runnable development implementation; not a v1 release.

- Add the Float32 Pillow/NumPy engine with all 17 internal Batch pipelines and the unchanged family sRGB module.
- Include the supplied multi-resolution AnaChroma icon unchanged for the GUI and native build icons.
- Add the German desktop GUI, automatic preview, keyboard/wheel navigation and recursive folder processing.
- Add a visible custom-method action, two 3×3 matrices, exact numeric entry, coefficient sliders and focused mouse-wheel editing.
- Add local preset storage, optional linear-light processing and individual RGB powers with a dedicated editor preview.
- Define brightness/contrast explicitly as shared sRGB factors; numeric entry only pending separately justified slider limits.
- Add Lanczos output sizes, JPEG 90/95 in 4:4:4, safe replacement and ExifTool metadata copying with corrected geometry/profile handling.
- Add cancellable external CIELab integration with separate PNG halves and isolated temporary files.
- Add independent FFmpeg reference comparisons, GUI/process/export tests and a portable build script with three-platform development CI.

Native CIELab binaries, practical photo validation and native Windows/macOS checks remain pending.
