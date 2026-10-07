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

## Regler und Referenzprogramme

Geprüft am 7. Oktober 2026. Die Programmdokumentationen liefern Orientierung für die Bedienung, aber keine gemeinsamen physikalischen Grenzen für alle Parameter. Ein Matrixkoeffizient ist ein Gewicht in einer Farbumrechnung, kein unmittelbar darstellbarer Lichtwert. Negative Gewichte und Gewichte über 1 können daher zu etablierten Verfahren gehören. Begrenzung der berechneten Bildkanäle und Begrenzung der Matrixeingabe sind getrennte Entscheidungen.

| Quelle | Belegter Befund | Bedeutung für AnaChroma |
| --- | --- | --- |
| [SPM: Optimised Anaglyph](https://stereo.jpn.org/eng/stphmkr/help/stereo_13.htm) | Ganzzahlige Matrixeingaben werden durch 1000 geteilt. Das Dubois-Beispiel enthält negative Werte und `1226`, also `1,226`. Allgemeine Eingabegrenzen sind dort nicht angegeben. | Tausendstel sind eine nachvollziehbare Grundlage für Matrix-Reglerschritte. Eine feste Grenze wie −2 bis +2 lässt sich daraus nicht ableiten. Bestehende Koeffizienten bleiben mit ihrer Genauigkeit erhalten. |
| [SPM: Color adjustment](https://stereo.jpn.org/eng/stphmkr/help/adjust_02.htm) | Die Hilfe nennt für den als Kontrast/Gamma bezeichneten Regler **0,01 bis 5,0**, Schritte **0,01**, und Echtzeitvorschau. Eine vollständige Gamma-Rechenvorschrift wird nicht genannt. | Dokumentierter Bedienbereich als Referenz. Erst die Richtung und Formel mit AnaChromas Kanalpotenz vergleichen; keine ungeprüfte Übernahme oder Gleichsetzung mit einem separaten Kontrastfaktor. |
| [Cosima: Anaglyphen-Parameter](https://www.cosima-3d.de/par_anaglyph_en.html) | Der Suchindex der offiziellen Seite nennt für `Brightness (/BN=1.0)` **0,0 bis 2,0**, neutral **1,0**. Für Kontrast nennt er neutral **1,0**, verstärkten Kontrast bei Werten unter 1 und verringerten bei Werten über 1. | Vorläufige Recherchehinweise, noch keine übernommenen Formeln oder Grenzen: Die Seite selbst war beim Abruf mit HTTP 502 nicht erreichbar. Vollständige Dokumentation bzw. Implementierung vor Übernahme prüfen. |
| [SPM: Ghost-reduced Anaglyph](https://stereo.jpn.org/eng/stphmkr/help/stereo_14.htm) | Beschreibt Lab- und RGB-Helligkeits-/Kontrastanpassungen und die Abhängigkeit von Brille und Wiedergabemedium. Liefert keine vollständigen Formeln und Reglergrenzen. | Daraus keine erfundenen Ghosting-Prozentwerte oder identische Nachimplementierung ableiten. |

Ergänzend dokumentiert [Adobe Photoshop: Channel Mixer](https://helpx.adobe.com/photoshop/desktop/adjust-color/selective-color-adjustments/mix-color-channels-with-channel-mixer.html) Kanalgewichte von −200 % bis +200 %. AnaChroma verwendet das als praktischen Reglerbereich **−2 bis +2**, zeigt aber direkte Koeffizienten. Die Batch liegt mit ihren Matrixwerten zwischen **−0,205 und 1,234**. Genauere und außerhalb liegende Zahlenwerte bleiben möglich; der Regler erweitert sich sichtbar. Das ist keine physikalische Begrenzung und keine Behauptung über SPM-Eingabegrenzen.

Das vom Nutzer genannte [Cosima-Papier „Anaglyphen“](http://www.cosima-3d.de/download/tn_anaglyphen.pdf) (2012, insbesondere Seiten 7–11) beschreibt eine Kalibrierung über Testfelder mit diskreten Auswahlzahlen und Anpassung des Grünanteils. Diese Einstellungen betreffen Brille, Druck bzw. Wiedergabe und sind keine allgemeine Skala für freie Matrixkoeffizienten. Daraus wird kein Ghosting-Regler abgeleitet.

Die Kanalpotenz `x^p` hat neutral `p=1`. Der Anfangsbereich **0,625 bis 1,25** umfasst die tatsächlich verwendeten, im Editor darstellbaren Batch-Potenzen: 0,625; 0,6666667; 0,75; 1; 1,25. Er ist für R/G/B gleichermaßen verfügbar; die bekannten Werte sind keine automatisch empfohlenen Korrekturen für Grün/Magenta oder Amber/Blau. Positive berechenbare Zahlenwerte erweitern den Bereich. SPMs Gammaformel wird damit nicht gleichgesetzt.

Helligkeit und Kontrast haben zunächst **Zahlenfelder ohne Schieberegler**. Neutral ist jeweils 1; die eigene, explizit dokumentierte affine sRGB-Formel ist in [PRESET_EDITOR.md](PRESET_EDITOR.md) festgehalten. Sie ist keine Cosima-/SPM-Nachimplementierung. Eingebaute Verfahren werden durch diese Editorentscheidungen nicht verändert.

Die implementierten Regler sind mit Formel, Rechenfarbraum, Reihenfolge, Neutralwert, Endpunkten, Schrittweite und Quelle in [PRESET_EDITOR.md](PRESET_EDITOR.md) dokumentiert. Eine abweichende eigene Bedienentscheidung wird als solche begründet. Eine Prozentanzeige benötigt eine ausdrücklich definierte Umrechnung; sie darf keine Präzision vortäuschen, die das Verfahren nicht besitzt.

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

`assets/ready.wav` wird unverändert aus SplatTricia übernommen. Dieselbe Datei ist auch in StereoFine vorhanden; der geprüfte Git-Blob lautet in beiden Projekten `260fb0d49982873a13dabd750b997448acb675ca` (503.364 Byte). Das von Christoph Müller bereitgestellte `assets/anachroma.ico` wird unverändert übernommen; enthalten sind 16, 24, 32, 40, 48, 64 und 256 px. Der SHA-256-Hash steht in `assets/ASSET_HASHES.txt`.

## CIELab PNG port and supplied SBS

The native CIELab source baseline is `mbrown1413/anaglyph` at `4db425343687f796b85f04ae204e05a43e5742f0`. `native/cielab/SOURCES.json` pins unchanged calculation/solver source hashes and the downloaded libpng/zlib source archives. The obsolete OpenCV image front end is replaced by a separately licensed GPL PNG CLI. The original Windows comparison binary is taken from the hash-verified AnaglyphBatch 1.0 release ZIP.

The user-supplied SBS image is preserved as `assets/anachroma.jpg` (2048 × 576 RGB; halves 1024 × 576). Its hash is in `assets/ASSET_HASHES.txt`; it serves as the live startup example and never enters the batch input list automatically.

Lossless CIELab reference PNGs were captured by the Windows comparison job in run `37641459630` and preserved with their individual SHA-256 values in `tests/fixtures/cielab_reference.json`. All platform tests compare against these actual executable outputs in addition to the fresh Windows executable comparison.
