# AnaChroma – Third-party notices

AnaChroma's own source code and original documentation are licensed under the MIT License (`LICENSE.txt`). Third-party software remains under its own licenses.

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

ExifTool copies metadata and remains separately licensed under its upstream Perl licensing terms. CIELab performs external Least Squares calculation. The official ExifTool distribution, support files, license information and corresponding source archive are included in portable packages. On Windows, its complete original launcher/Perl distribution is retained; Linux/macOS require system Perl. Native CIELab is built from pinned sources and supplied as a separate program, with the corresponding full source archive and GPL-3.0, levmar, libpng and zlib licenses in `tools/cielab`. libpng/zlib and the Windows MSVC runtime are linked statically; operating-system runtime dependencies remain. AnaChroma's MIT License does not relicense CIELab.

CIELab is based on the [CIELab Anaglyph Tool](https://github.com/mbrown1413/anaglyph). The original calculation is GPL-3.0 and levmar is GPL-2.0-or-later. The PNG interface uses libpng and zlib; complete corresponding sources and license material accompany the binary.
