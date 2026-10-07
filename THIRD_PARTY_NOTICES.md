# AnaChroma – Third-party notices

AnaChroma's own source code and original documentation are licensed under the MIT License (`LICENSE.txt`). Third-party software remains under its own licenses.

## Current repository

This initial repository contains documentation and the unchanged `assets/ready.wav` completion sound reused from the StereoFine/SplatTricia project family. It does not yet contain an application, an embedded Python runtime or external tool binaries.

## Planned runtime components

| Component | Purpose |
| --- | --- |
| Python and Tcl/Tk | Application runtime and native GUI foundation |
| CustomTkinter | Desktop interface |
| Pillow | Image loading, EXIF orientation, resizing and JPEG output |
| NumPy | Float image processing and matrix arithmetic |
| ExifTool | External metadata copying |
| CIELab Anaglyph Tool | External CIELab Least Squares calculation |

Exact versions, transitive dependencies and corresponding license material will be recorded when the implementation and release dependencies are fixed. This table is a development plan, not a list of components already bundled in a release.

ExifTool and CIELab will remain visibly separate external tools. Their original license and distribution material must accompany distributed binaries. AnaChroma's MIT License does not relicense these tools or their dependencies.

## Reference projects

- [AnaglyphBatch](https://github.com/muelli1975/AnaglyphBatch): method definitions and reference processing pipelines
- [SplatTricia](https://github.com/muelli1975/SplatTricia): existing sRGB transfer module, interface conventions and completion sound
- [StereoFine](https://github.com/muelli1975/StereoFine): navigation, worker, metadata and packaging conventions
- [CIELab Anaglyph Tool](https://github.com/mbrown1413/anaglyph): upstream source for the external calculation

The first three projects use the MIT License for their own code and original documentation. Upstream CIELab code and its OpenCV/levmar dependencies require their own license material when supplied; see the upstream distributions for the complete terms.
