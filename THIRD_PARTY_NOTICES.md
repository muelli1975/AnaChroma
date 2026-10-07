# AnaChroma – Third-party notices

AnaChroma's own source code and original documentation are licensed under the MIT License (`LICENSE.txt`). Third-party software remains under its own licenses.

## Source repository

- `src/anachroma/color_transfer.py` is copied unchanged from [SplatTricia](https://github.com/muelli1975/SplatTricia/tree/d9967e000ede99e63b5859d7405c9f5158c66cf0), by Christoph Müller, MIT licensed.
- `tests/reference_batch.bat` is an unchanged reference from [AnaglyphBatch](https://github.com/muelli1975/AnaglyphBatch/tree/8ef0a5dc4a5fbea865bab120d566161a0fb5b3fa), by Christoph Müller, MIT licensed. It is used for independent validation, not as the runtime engine.
- `assets/ready.wav` is the unchanged completion sound reused from the StereoFine/SplatTricia project family. Its provenance/hash is recorded in `docs/REFERENCE_BASELINE.md` and `assets/ASSET_HASHES.txt`.

`native/cielab/upstream` contains unchanged GPL CIELab and levmar sources. `native/cielab/main.c`, `compat/cv.h`, and its build instructions form a separate GPL-3.0-or-later PNG port; this directory is explicitly excluded from AnaChroma’s MIT licensing. The source repository contains no external binaries and no embedded Python runtime. The supplied `assets/anachroma.jpg` is preserved unchanged; its SHA-256 is recorded with the icon and sound.

## Runtime and development packages

| Component | Purpose | License material |
| --- | --- | --- |
| Python | Bundled interpreter in portable builds | Python Software Foundation and included historical licenses |
| Tcl/Tk | Native GUI foundation | Tcl/Tk license terms in the respective runtime distribution |
| CustomTkinter 5.2.2 | Desktop interface, fonts/assets | Included MIT license; preserve bundled asset license material |
| Pillow | Load, orient, resize and save images; sRGB profile generation | MIT-CMU and included native-library notices |
| NumPy | Float image processing and matrix arithmetic | BSD license and bundled native-library notices |
| darkdetect | CustomTkinter dependency | BSD-3-Clause |
| packaging | Version parsing dependency | Apache-2.0 or BSD-2-Clause |

`requirements-build.txt` pins the tested build inputs. `scripts/build.py` records actual runtime versions and copies installed library license files to `licenses/`; native dependencies can vary between target platforms. Review the complete material for each distributed package. The table does not relicense bundled fonts, native libraries or other assets.

PyInstaller and its hooks build the packages; pytest and optional FFmpeg validate them. These are not AnaChroma's normal processing engine. PyInstaller's bootloader is distributed under its upstream license and exception permitting distribution of generated applications; retain applicable distribution material.

## External tools

ExifTool copies metadata and remains separately licensed under its upstream Perl licensing terms. CIELab performs external Least Squares calculation. ExifTool is not bundled. Native CIELab is built from pinned sources and supplied as a separate program, with the corresponding full source archive and GPL-3.0, levmar, libpng and zlib licenses in `tools/cielab`. libpng/zlib and the Windows MSVC runtime are linked statically; operating-system runtime dependencies remain. AnaChroma's MIT License does not relicense CIELab.

## Reference projects

- [AnaglyphBatch](https://github.com/muelli1975/AnaglyphBatch): method definitions and processing pipelines
- [SplatTricia](https://github.com/muelli1975/SplatTricia): sRGB transfer module, interface conventions and completion sound
- [StereoFine](https://github.com/muelli1975/StereoFine): navigation, worker, metadata and packaging conventions
- [CIELab Anaglyph Tool](https://github.com/mbrown1413/anaglyph): upstream source for the external calculation

The first three projects use the MIT License for their own code and original documentation. Upstream CIELab is GPL-3.0 and levmar is GPL-2.0-or-later. The PNG port uses libpng and zlib in place of OpenCV; complete corresponding sources and their own license material accompany the binary.
