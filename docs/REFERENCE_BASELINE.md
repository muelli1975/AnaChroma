# AnaChroma – Technische Quellgrundlage

Geprüft am 7. Oktober 2026. Diese Referenzen legen die Grundlage des ersten Entwicklungsstands fest. Spätere Änderungen der Fremdrepositories werden bewusst abgeglichen, nicht automatisch übernommen.

## Geprüfte Stände

| Projekt | Commit | Übernahme bzw. Orientierung |
| --- | --- | --- |
| [AnaglyphBatch](https://github.com/muelli1975/AnaglyphBatch/tree/8ef0a5dc4a5fbea865bab120d566161a0fb5b3fa) | `8ef0a5dc4a5fbea865bab120d566161a0fb5b3fa` | Verfahren, Matrixwerte, Modi, Suffixe, Größen und Ordnerabbildung |
| [SplatTricia](https://github.com/muelli1975/SplatTricia/tree/d9967e000ede99e63b5859d7405c9f5158c66cf0) | `d9967e000ede99e63b5859d7405c9f5158c66cf0` | Kleines sRGB-Modul, Anaglyphenkern, Designstandard, Fortschritt und Sound |
| [StereoFine](https://github.com/muelli1975/StereoFine/tree/fb67a96cc231d97cf09febe8b844ea6d13371fd9) | `fb67a96cc231d97cf09febe8b844ea6d13371fd9` | Navigation, Worker, Metadaten und plattformübergreifendes Packaging |

## Aktuelle Verfahren

Quelle: [AnaglyphBatch_DE.bat](https://github.com/muelli1975/AnaglyphBatch/blob/8ef0a5dc4a5fbea865bab120d566161a0fb5b3fa/AnaglyphBatch_DE.bat), insbesondere `:set_matrix_definition` und `:process_file`.

| Nr. | Anzeige | Suffix | Batch-Modus |
| --- | --- | --- | --- |
| 1 | Dubois LCD (Sanders/McAllister) + rot | `dubois_lcd` | `linear` |
| 2 | Dubois | `dubois` | `linear` |
| 3 | Optimized (Peter Wimmer) | `wimmer` | `srgb` |
| 4 | Cosima AnaglyphType=3 (Gerhard P. Herbig) | `cosima3` | `linear` |
| 5 | Cosima AnaglyphType=4 (Gerhard P. Herbig) | `cosima4` | `linear` |
| 6 | Compromise (Jure Ahtik) | `compromise` | `srgb` |
| 7 | iaian7 Anachrome (John Einselen) | `iaian7` | `iaian7` |
| 8 | Rendepth (Andres Hernandez) | `rendepth` | `rendepth` |
| 9 | Rendepth 2 (Andres Hernandez) | `rendepth2` | `rendepth` |
| 10 | Color | `color` | `srgb` |
| 11 | Half-Color | `halfcolor` | `srgb` |
| 12 | Grey | `grey` | `srgb` |
| 13 | Oldschool | `oldschool` | `srgb` |
| 14 | Frans van den Poel | `vdp` | `srgb` |
| 15 | John Wattie | `wattie` | `srgb` |
| 16 | CIELab Least Squares (David McAllister) | `cielab` | `cielab` |
| 17 | Dubois grün/magenta (GM) | `dubois_gm` | `linear` |
| 18 | Dubois amber/blau (YB) | `dubois_yb` | `linear` |

Die längeren Cosima-Beschreibungen stehen im Batch-Menü. Die Darstellung im kompakten GUI kann gekürzt werden; Werte, Verfahrensidentität und Suffixe bleiben unverändert. Die Batch erlaubt mehrere Verfahren, AnaChroma v1 wählt eines.

## Farbverarbeitung

- [SplatTricia color_transfer.py](https://github.com/muelli1975/SplatTricia/blob/d9967e000ede99e63b5859d7405c9f5158c66cf0/src/splattricia/color_transfer.py): eigenständiges kleines NumPy-Modul mit Float32-sRGB-Decodierung und -Encodierung.
- [StereoFine color_transfer.py](https://github.com/muelli1975/StereoFine/blob/fb67a96cc231d97cf09febe8b844ea6d13371fd9/stereofine/color_transfer.py): gleiche Transferformeln, zusätzlich separate Farbangleichungsfunktionen.
- Vergleich beider Transferfunktionen über je 65.536 gleichmäßig verteilte Float32-Werte von 0 bis 1: exakte Übereinstimmung im geprüften Lauf, maximale Abweichung 0. Das ist eine Prüfung dieser Werte und keine Behauptung über sämtliche möglichen Eingaben.
- [SplatTricia anaglyph.py](https://github.com/muelli1975/SplatTricia/blob/d9967e000ede99e63b5859d7405c9f5158c66cf0/src/splattricia/anaglyph.py) und [StereoFine anaglyph.py](https://github.com/muelli1975/StereoFine/blob/fb67a96cc231d97cf09febe8b844ea6d13371fd9/stereofine/anaglyph.py): identische Dubois-LCD-Matrizen, separate Begrenzung beider Beiträge, Rotpotenz 0,75 nach sRGB-Encodierung; Grey direkt in sRGB.

Bei der Python-Portierung müssen zusätzlich die tatsächlichen FFmpeg-Filterformate, Rundung, Clipping und Gammafolgen anhand von Referenzausgaben geprüft werden. Ein gleicher Koeffizientensatz allein garantiert kein pixelgleiches Ergebnis. JPEG-Differenzen werden getrennt vom Rechenkern beurteilt.

## Größen und CIELab

Die Batch passt 1080p in 1920 × 1080 und 2160p in 3840 × 2160 ein, jeweils mit `force_original_aspect_ratio=decrease`. 2048 lange Seite entspricht dem Einpassen in 2048 × 2048. Diese Filteroption allein bedeutet nicht, dass kleine Quellen niemals vergrößert werden.

Normale Verfahren skalieren nach der Berechnung. CIELab skaliert beide Halbbilder vor der Berechnung und ruft dann `cielab <left.png> <right.png> -o <output.png>` auf. Die Reihenfolge ist Teil der Referenzpipeline.

Upstream: [mbrown1413/anaglyph](https://github.com/mbrown1413/anaglyph). README und Makefile beschreiben eine native C-Buildkette mit OpenCV und levmar sowie optionale OpenMP-/LAPACK-Unterstützung. Die vorhandenen OpenCV-Anbindungen sind älter; neue Windows-/Linux-/macOS-Builds sind noch zu prüfen.

## Metadaten, Oberfläche und Builds

- [SplatTricia metadata.py](https://github.com/muelli1975/SplatTricia/blob/d9967e000ede99e63b5859d7405c9f5158c66cf0/src/splattricia/metadata.py): Vorschauen und Orientation ausschließen, externen Prozess mit Zeitlimit verwenden.
- [StereoFine metadata.py](https://github.com/muelli1975/StereoFine/blob/fb67a96cc231d97cf09febe8b844ea6d13371fd9/stereofine/metadata.py): lokale ExifTool-Suche für mehrere Plattformen, zusätzlich MPF ausschließen, Metadatenfehler als Warnung behandeln.
- [Designstandard](https://github.com/muelli1975/SplatTricia/blob/d9967e000ede99e63b5859d7405c9f5158c66cf0/DESIGN_STANDARD_STEREOTOOLS.txt): gemeinsame Palette, Buttonzustände, getrennte Dialoggedächtnisse und Vorschaugestaltung.
- StereoFine-Navigation: `◀ Vorheriges` / `Nächstes ▶` sowie Bild auf/Bild ab; Pfeiltasten dienen dort der Justage, Mausradnavigation ist im geprüften GUI-Code nicht vorhanden.
- [StereoFine worker.py](https://github.com/muelli1975/StereoFine/blob/fb67a96cc231d97cf09febe8b844ea6d13371fd9/stereofine/worker.py): Jobs mit IDs, Nachrichtenqueue und Abbruchtoken.
- [StereoFine Build-Workflow](https://github.com/muelli1975/StereoFine/blob/fb67a96cc231d97cf09febe8b844ea6d13371fd9/.github/workflows/build-release.yml): Vorlage für Windows, Linux und macOS Apple Silicon/Intel mit externem ExifTool. Verfügbarkeit eines Builds ersetzt keinen Desktop-Test.

## Ressourcen

`assets/ready.wav` wird unverändert aus SplatTricia übernommen. Dieselbe Datei ist auch in StereoFine vorhanden; der geprüfte Git-Blob lautet in beiden Projekten `260fb0d49982873a13dabd750b997448acb675ca` (503.364 Byte). Das AnaChroma-Icon wird später von Christoph Müller bereitgestellt.
