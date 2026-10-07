# AnaChroma – Third-party notices

AnaChroma's own source code and original documentation are licensed under the MIT License (`LICENSE.txt`). Third-party software remains under its own licenses.

## Source repository

- `src/anachroma/color_transfer.py` is copied unchanged from [SplatTricia](https://github.com/muelli1975/SplatTricia/tree/d9967e000ede99e63b5859d7405c9f5158c66cf0), by Christoph Müller, MIT licensed.
- `tests/reference_batch.bat` is an unchanged reference from [AnaglyphBatch](https://github.com/muelli1975/AnaglyphBatch/tree/8ef0a5dc4a5fbea865bab120d566161a0fb5b3fa), by Christoph Müller, MIT licensed. It is used for independent validation, not as the runtime engine.
- `assets/ready.wav` is the unchanged completion sound reused from the StereoFine/SplatTricia project family. Its provenance/hash is recorded in `docs/REFERENCE_BASELINE.md` and `assets/ASSET_HASHES.txt`.

The repository contains no external ExifTool/CIELab binaries and no embedded Python runtime.

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

ExifTool copies metadata and remains separately licensed under its upstream Perl licensing terms. CIELab performs external Least Squares calculation. Neither is bundled in the first development packages. Complete licenses and distribution material must accompany any later supplied binaries, including required native dependencies. AnaChroma's MIT License does not relicense them.

## Reference projects

- [AnaglyphBatch](https://github.com/muelli1975/AnaglyphBatch): method definitions and processing pipelines
- [SplatTricia](https://github.com/muelli1975/SplatTricia): sRGB transfer module, interface conventions and completion sound
- [StereoFine](https://github.com/muelli1975/StereoFine): navigation, worker, metadata and packaging conventions
- [CIELab Anaglyph Tool](https://github.com/mbrown1413/anaglyph): upstream source for the external calculation

The first three projects use the MIT License for their own code and original documentation. Upstream CIELab code and its OpenCV/levmar dependencies require their own license material when supplied; see the upstream distributions for the complete terms.
