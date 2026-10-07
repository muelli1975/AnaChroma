# CIELab PNG port

This separately executed GPL-3.0-or-later tool builds the original CIELab
Least Squares method from `mbrown1413/anaglyph` at commit
`4db425343687f796b85f04ae204e05a43e5742f0`. `SOURCES.json` records hashes
for the unchanged color computation and levmar solver sources.

The port replaces the obsolete OpenCV 2.4 image/video front end with a
PNG-only command line. It accepts two equally sized RGB8 PNG halves:

```sh
cielab left.png right.png -o output.png
```

No OpenCV DLLs, video modes, camera modes or display window are included.
The interface matches the calls made by AnaChroma and AnaglyphBatch.
Do not apply additional sRGB transfer functions to the halves; the method
contains its own color transformations. Resize both halves before calling
the tool when a smaller CIELab output is requested. Resizing is performed
by the calling application, not by this executable.

The solver, color/filter constants and iteration limits remain unchanged.
Input RGB is mapped to the upstream BGR scalar convention, and output is
rounded to nearest (ties to even) and clipped to RGB8 as by OpenCV `cvSet2D`.
Compiler/platform floating-point differences must be checked independently.
The Windows CI compares this port with the executable shipped in
AnaglyphBatch 1.0; see the recorded validation results before replacing it.

## Build

From the AnaChroma repository, with a C compiler and pinned Python build
requirements installed:

```sh
python scripts/build_cielab.py
```

CMake builds libpng 1.6.59 and zlib 1.3.2 statically from hash-verified source
archives. The executable is placed in `tools/cielab`. It has no OpenCV or
libpng/zlib shared-library requirement. Operating-system runtime libraries
remain platform dependencies. Windows uses the static MSVC runtime.

Every distributed build contains the matching `cielab-source.tar.gz`, source
provenance, and full license texts. To build from that archive offline:

```sh
tar -xzf cielab-source.tar.gz
cmake -S cielab-source/native -B objects -DCMAKE_BUILD_TYPE=Release -DCIELAB_DEPS="<absolute-path>/cielab-source/dependencies"
cmake --build objects --config Release --target cielab
```

Upstream CIELab is GPL-3.0; levmar is GPL-2.0-or-later. The port is licensed
under GPL-3.0-or-later, with the combined executable distributed under GPL-3.0.
libpng and zlib retain their own permissive licenses. This does not relicense
the separately communicating AnaChroma Python application.
